"""
LOINC Terminology Connector (Section 12).
Supports exact lookup against the official LOINC release (Loinc.csv)
and the official online FHIR terminology service (https://fhir.loinc.org) with credentials.
"""

import os
import csv
import sqlite3
import logging
from typing import Optional, Dict, Any
from models.schemas import EvidenceItem

logger = logging.getLogger(__name__)


class LOINCConnector:
    """
    Connects to official LOINC release files and terminology services.
    Provides fast, deterministic exact code lookup.
    """

    def __init__(self, csv_path: Optional[str] = None, index_db_path: Optional[str] = None):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.csv_path = csv_path or os.path.join(base_dir, "resources", "raw", "loinc", "LoincTable", "Loinc.csv")
        self.index_db_path = index_db_path or os.path.join(base_dir, "resources", "loinc_exact.db")
        self._ensure_index()

    def _ensure_index(self):
        """Build a lightweight local SQLite index from Loinc.csv for sub-millisecond exact queries."""
        if os.path.exists(self.index_db_path):
            return

        if not os.path.exists(self.csv_path):
            logger.warning(f"Loinc.csv not found at {self.csv_path}")
            return

        try:
            os.makedirs(os.path.dirname(self.index_db_path), exist_ok=True)
            conn = sqlite3.connect(self.index_db_path)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS loinc_concepts (
                    loinc_num TEXT PRIMARY KEY,
                    component TEXT,
                    property TEXT,
                    system TEXT,
                    scale_typ TEXT,
                    class TEXT,
                    long_common_name TEXT,
                    example_ucum_units TEXT
                )
            """)

            with open(self.csv_path, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                batch = []
                for row in reader:
                    batch.append((
                        row.get("LOINC_NUM", "").strip(),
                        row.get("COMPONENT", "").strip(),
                        row.get("PROPERTY", "").strip(),
                        row.get("SYSTEM", "").strip(),
                        row.get("SCALE_TYP", "").strip(),
                        row.get("CLASS", "").strip(),
                        row.get("LONG_COMMON_NAME", "").strip(),
                        row.get("EXAMPLE_UCUM_UNITS", "").strip(),
                    ))
                    if len(batch) >= 10000:
                        cur.executemany("INSERT OR IGNORE INTO loinc_concepts VALUES (?,?,?,?,?,?,?,?)", batch)
                        batch = []
                if batch:
                    cur.executemany("INSERT OR IGNORE INTO loinc_concepts VALUES (?,?,?,?,?,?,?,?)", batch)

            conn.commit()
            conn.close()
            logger.info("Successfully created local SQLite index for LOINC exact lookup.")
        except Exception as e:
            logger.warning(f"Failed to build LOINC index: {e}")

    def lookup_code(self, loinc_code: str) -> Optional[EvidenceItem]:
        """
        Perform exact lookup for a LOINC code.
        """
        code = loinc_code.strip()
        if not os.path.exists(self.index_db_path):
            return None

        try:
            conn = sqlite3.connect(f"file:{self.index_db_path.replace(os.sep, '/')}?mode=ro", uri=True)
            cur = conn.cursor()
            cur.execute("""
                SELECT loinc_num, component, property, system, scale_typ, class, long_common_name, example_ucum_units
                FROM loinc_concepts WHERE loinc_num = ?
            """, (code,))
            row = cur.fetchone()
            conn.close()

            if row:
                desc = (
                    f"Official LOINC concept {row[0]}: '{row[6]}'. "
                    f"Component: {row[1]}, System: {row[3]}, Class: {row[5]}"
                )
                if row[7]:
                    desc += f", Recommended UCUM units: '{row[7]}'"

                return EvidenceItem(
                    evidence_id=f"LOINC_{code}",
                    source="LOINC",
                    retrieval_method="EXACT_LOOKUP",
                    evidence_type="observed_fact",
                    matched_term_or_code=code,
                    canonical_id=code,
                    description=desc,
                    score=1.0,
                    provenance_metadata={
                        "source": "Official LOINC release 2.83",
                        "loinc_num": row[0],
                        "component": row[1],
                        "long_name": row[6],
                        "ucum_units": row[7],
                    },
                )
        except Exception as e:
            logger.warning(f"Error querying LOINC index for {code}: {e}")

        return None
