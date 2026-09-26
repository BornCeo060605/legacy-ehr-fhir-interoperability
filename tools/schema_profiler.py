"""
Deterministic Schema Profiler for Legacy EHR Databases.
Operates exclusively in READ-ONLY mode on SQLite databases.
Gathers facts, statistics, relationships, and distinguishes observed facts from inferences.
"""

import os
import re
import sqlite3
import hashlib
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime

from models.schemas import (
    ColumnFact,
    TableProfile,
    DatabaseProfile,
    RelationshipFact,
    NumericStats,
    DateStats,
)


class SchemaProfiler:
    """
    Deterministic schema profiler for inspecting unfamiliar legacy SQLite EHR databases.
    Enforces strict read-only access and objective evidence collection.
    """

    def __init__(self, db_path: str):
        self.db_path = os.path.abspath(db_path)
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
        self.db_name = os.path.basename(self.db_path)

    def _get_ro_connection(self) -> sqlite3.Connection:
        """Create a guaranteed read-only SQLite connection using URI mode."""
        # URI mode ?mode=ro prevents any write, schema modification, or transaction creation
        uri_path = f"file:{self.db_path.replace(os.sep, '/')}?mode=ro"
        conn = sqlite3.connect(uri_path, uri=True, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _compute_checksum(self) -> str:
        """Compute SHA256 checksum of the database file for auditability and reproducibility."""
        hasher = hashlib.sha256()
        with open(self.db_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _detect_date_characteristics(self, sample_values: List[str]) -> Optional[DateStats]:
        """Detect if values match date or timestamp patterns deterministically."""
        date_patterns = [
            (r"^\d{4}-\d{2}-\d{2}$", "%Y-%m-%d"),
            (r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", "%Y-%m-%d %H:%M:%S"),
            (r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", "ISO8601"),
            (r"^\d{2}/\d{2}/\d{4}$", "%m/%d/%Y"),
            (r"^\d{8}$", "%Y%m%d"),
        ]
        valid_dates = []
        matched_format = None

        for val in sample_values:
            val_str = str(val).strip()
            for pattern, fmt in date_patterns:
                if re.match(pattern, val_str):
                    valid_dates.append(val_str)
                    matched_format = fmt
                    break

        if len(valid_dates) >= max(1, len(sample_values) // 2) and matched_format:
            try:
                sorted_dates = sorted(valid_dates)
                return DateStats(
                    min_date=sorted_dates[0],
                    max_date=sorted_dates[-1],
                    likely_format=matched_format,
                )
            except Exception:
                return DateStats(likely_format=matched_format)
        return None

    def profile_column(
        self, conn: sqlite3.Connection, table_name: str, col_info: Dict[str, Any], total_rows: int
    ) -> ColumnFact:
        """Profile a single column collecting deterministic statistics and sample values."""
        col_name = col_info["name"]
        declared_type = col_info["type"].upper() if col_info["type"] else "UNKNOWN"
        is_nullable = not bool(col_info["notnull"])
        is_pk = bool(col_info["pk"])

        cursor = conn.cursor()

        # Null and non-null counts
        escaped_col = f'"{col_name}"'
        escaped_tbl = f'"{table_name}"'
        
        query = f"""
            SELECT 
                COUNT(*) - COUNT({escaped_col}) AS null_count,
                COUNT({escaped_col}) AS non_null_count,
                COUNT(DISTINCT {escaped_col}) AS distinct_count
            FROM {escaped_tbl}
        """
        cursor.execute(query)
        stats = cursor.fetchone()
        null_count = stats["null_count"]
        non_null_count = stats["non_null_count"]
        distinct_count = stats["distinct_count"]

        null_percentage = (null_count / total_rows * 100.0) if total_rows > 0 else 0.0
        uniqueness_ratio = (distinct_count / non_null_count) if non_null_count > 0 else 0.0
        is_unique = (distinct_count == non_null_count and non_null_count > 0)

        # Sample values (up to 5 distinct non-null representative values)
        sample_query = f"""
            SELECT DISTINCT {escaped_col}
            FROM {escaped_tbl}
            WHERE {escaped_col} IS NOT NULL
            LIMIT 5
        """
        cursor.execute(sample_query)
        sample_rows = cursor.fetchall()
        sample_values = [str(r[0]) for r in sample_rows]

        # Top frequent values for categorical insight
        freq_query = f"""
            SELECT {escaped_col}, COUNT(*) as cnt
            FROM {escaped_tbl}
            WHERE {escaped_col} IS NOT NULL
            GROUP BY {escaped_col}
            ORDER BY cnt DESC
            LIMIT 5
        """
        cursor.execute(freq_query)
        freq_rows = cursor.fetchall()
        top_frequent = {str(r[0]): r["cnt"] for r in freq_rows}

        # Numeric stats if applicable
        numeric_stats = None
        if non_null_count > 0:
            num_query = f"""
                SELECT 
                    MIN({escaped_col}) as min_val,
                    MAX({escaped_col}) as max_val,
                    AVG({escaped_col}) as avg_val
                FROM {escaped_tbl}
                WHERE {escaped_col} IS NOT NULL AND typeof({escaped_col}) IN ('integer', 'real')
            """
            try:
                cursor.execute(num_query)
                num_row = cursor.fetchone()
                if num_row and num_row["min_val"] is not None:
                    numeric_stats = NumericStats(
                        min=float(num_row["min_val"]),
                        max=float(num_row["max_val"]),
                        mean=float(num_row["avg_val"]) if num_row["avg_val"] is not None else None,
                        is_integer="INT" in declared_type,
                    )
            except Exception:
                pass

        # Date stats
        date_stats = self._detect_date_characteristics(sample_values)

        # Summary statement distinguishing observed facts
        summary_parts = [
            f"Observed type '{declared_type}'",
            f"{distinct_count} distinct values across {non_null_count} non-null rows ({null_percentage:.1f}% null)",
        ]
        if is_pk:
            summary_parts.append("Declared PRIMARY KEY in schema")
        elif is_unique:
            summary_parts.append("100% unique non-null values (candidate identifier)")

        if sample_values:
            samples_str = ", ".join(f"'{s}'" for s in sample_values[:3])
            summary_parts.append(f"Samples: [{samples_str}]")

        return ColumnFact(
            table_name=table_name,
            column_name=col_name,
            data_type=declared_type,
            is_nullable=is_nullable,
            is_declared_pk=is_pk,
            row_count=total_rows,
            null_count=null_count,
            non_null_count=non_null_count,
            null_percentage=round(null_percentage, 2),
            distinct_count=distinct_count,
            uniqueness_ratio=round(uniqueness_ratio, 4),
            is_unique=is_unique,
            sample_values=sample_values,
            numeric_stats=numeric_stats,
            date_stats=date_stats,
            top_frequent_values=top_frequent,
            observed_fact_summary="; ".join(summary_parts),
        )

    def profile_table(self, conn: sqlite3.Connection, table_name: str) -> TableProfile:
        """Profile a single table, its columns, primary keys, and declared foreign keys."""
        cursor = conn.cursor()

        # Row count
        cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        total_rows = cursor.fetchone()[0]

        # Table columns via PRAGMA table_info
        cursor.execute(f'PRAGMA table_info("{table_name}")')
        cols_info = [dict(row) for row in cursor.fetchall()]

        columns: Dict[str, ColumnFact] = {}
        declared_pks: List[str] = []

        for col_info in cols_info:
            col_fact = self.profile_column(conn, table_name, col_info, total_rows)
            columns[col_info["name"]] = col_fact
            if col_info["pk"]:
                declared_pks.append(col_info["name"])

        # Candidate primary keys (100% unique, non-null, non-empty)
        candidate_pks = [
            c_name
            for c_name, c_fact in columns.items()
            if c_fact.is_unique and c_fact.null_count == 0 and c_fact.non_null_count > 0
        ]

        # Declared foreign keys via PRAGMA foreign_key_list
        cursor.execute(f'PRAGMA foreign_key_list("{table_name}")')
        fk_rows = cursor.fetchall()
        declared_fks = []
        for r in fk_rows:
            declared_fks.append(
                {
                    "id": r["id"],
                    "from_column": r["from"],
                    "target_table": r["table"],
                    "target_column": r["to"],
                    "on_update": r["on_update"],
                    "on_delete": r["on_delete"],
                }
            )

        return TableProfile(
            table_name=table_name,
            row_count=total_rows,
            column_count=len(columns),
            columns=columns,
            declared_primary_keys=declared_pks,
            declared_foreign_keys=declared_fks,
            candidate_primary_keys=candidate_pks,
        )

    def detect_value_overlaps(
        self, conn: sqlite3.Connection, tables: Dict[str, TableProfile]
    ) -> List[RelationshipFact]:
        """
        Detect value-overlap relationships across tables.
        Calculates distinct value containment and Jaccard similarity.
        Strictly distinguishes OBSERVED FACT from INFERENCE.
        """
        relationships: List[RelationshipFact] = []
        cursor = conn.cursor()

        # Cache distinct non-null values for identifier-like or code-like columns
        # To remain fast and memory efficient, only check columns with >= 2 distinct values
        column_value_sets: Dict[Tuple[str, str], Set[str]] = {}

        for tbl_name, tbl_prof in tables.items():
            for col_name, col_fact in tbl_prof.columns.items():
                if 2 <= col_fact.distinct_count <= 50000:
                    cursor.execute(
                        f'SELECT DISTINCT "{col_name}" FROM "{tbl_name}" WHERE "{col_name}" IS NOT NULL'
                    )
                    column_value_sets[(tbl_name, col_name)] = {
                        str(r[0]).strip() for r in cursor.fetchall() if r[0] is not None
                    }

        checked_pairs = set()
        col_list = list(column_value_sets.keys())

        for i in range(len(col_list)):
            for j in range(len(col_list)):
                if i == j:
                    continue
                src_tbl, src_col = col_list[i]
                tgt_tbl, tgt_col = col_list[j]

                if src_tbl == tgt_tbl:
                    continue

                pair_key = (src_tbl, src_col, tgt_tbl, tgt_col)
                if pair_key in checked_pairs:
                    continue
                checked_pairs.add(pair_key)

                src_vals = column_value_sets[(src_tbl, src_col)]
                tgt_vals = column_value_sets[(tgt_tbl, tgt_col)]

                overlap = src_vals.intersection(tgt_vals)
                overlap_count = len(overlap)

                if overlap_count >= 3:
                    src_containment = overlap_count / len(src_vals)
                    tgt_containment = overlap_count / len(tgt_vals)
                    union_count = len(src_vals.union(tgt_vals))
                    jaccard = overlap_count / union_count if union_count > 0 else 0.0

                    # Filter for meaningful relationships:
                    # E.g. Significant containment (>= 50%) or strong Jaccard (>= 0.3)
                    # or matching column name stems
                    names_similar = (
                        src_col.lower() in tgt_col.lower()
                        or tgt_col.lower() in src_col.lower()
                        or src_col.split("_")[-1].lower() == tgt_col.split("_")[-1].lower()
                    )

                    if src_containment >= 0.5 or jaccard >= 0.3 or (names_similar and src_containment >= 0.2):
                        rel_type = (
                            "VALUE_OVERLAP_INCLUSION"
                            if src_containment >= 0.95
                            else "VALUE_OVERLAP_PARTIAL"
                        )

                        observed = (
                            f"Observed {overlap_count} overlapping distinct values between "
                            f"{src_tbl}.{src_col} and {tgt_tbl}.{tgt_col} "
                            f"(Source containment: {src_containment:.1%}, Target containment: {tgt_containment:.1%})"
                        )

                        # Formulate cautious, evidence-backed inference
                        is_patient_target = (
                            any(pt in tgt_tbl.upper() for pt in ["PATIENT", "PT_MST", "PERSON", "DEMOGRAPHIC"])
                            or any(pc in tgt_col.upper() for pc in ["PID", "PATIENT", "PAT_ID", "PERSON_ID"])
                        )
                        if src_containment >= 0.95 and is_patient_target:
                            inference = (
                                f"Values in {src_tbl}.{src_col} are fully contained in {tgt_tbl}.{tgt_col}. "
                                "Consistent with a foreign-key patient reference."
                            )
                        elif src_containment >= 0.90:
                            inference = (
                                f"Strong value containment ({src_containment:.1%}) suggests "
                                f"{src_tbl}.{src_col} acts as a foreign reference to {tgt_tbl}.{tgt_col}."
                            )
                        else:
                            inference = (
                                f"Moderate value overlap ({src_containment:.1%}) indicates shared domain or concept pool."
                            )

                        relationships.append(
                            RelationshipFact(
                                source_table=src_tbl,
                                source_column=src_col,
                                target_table=tgt_tbl,
                                target_column=tgt_col,
                                relationship_type=rel_type,
                                overlap_count=overlap_count,
                                source_distinct_count=len(src_vals),
                                target_distinct_count=len(tgt_vals),
                                source_containment=round(src_containment, 4),
                                target_containment=round(tgt_containment, 4),
                                jaccard_similarity=round(jaccard, 4),
                                observed_fact=observed,
                                inference=inference,
                            )
                        )

        # Sort relationships by containment and overlap count
        relationships.sort(key=lambda r: (r.source_containment, r.overlap_count), reverse=True)
        return relationships

    def profile_database(self) -> DatabaseProfile:
        """Run the complete deterministic profiling pipeline."""
        checksum = self._compute_checksum()
        conn = self._get_ro_connection()

        try:
            cursor = conn.cursor()

            # Get list of user tables (exclude sqlite system tables)
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
            table_names = [row[0] for row in cursor.fetchall()]

            tables: Dict[str, TableProfile] = {}
            all_declared_fks: List[Dict[str, Any]] = []
            candidate_identifiers: List[Dict[str, Any]] = []

            for tbl_name in table_names:
                tbl_profile = self.profile_table(conn, tbl_name)
                tables[tbl_name] = tbl_profile

                for fk in tbl_profile.declared_foreign_keys:
                    all_declared_fks.append({"source_table": tbl_name, **fk})

                for pk in tbl_profile.candidate_primary_keys:
                    candidate_identifiers.append(
                        {
                            "table_name": tbl_name,
                            "column_name": pk,
                            "is_declared_pk": pk in tbl_profile.declared_primary_keys,
                            "row_count": tbl_profile.row_count,
                        }
                    )

            # Value overlap detection across tables
            overlaps = self.detect_value_overlaps(conn, tables)

            summary = {
                "total_tables": len(tables),
                "total_columns": sum(t.column_count for t in tables.values()),
                "total_rows": sum(t.row_count for t in tables.values()),
                "declared_fk_count": len(all_declared_fks),
                "discovered_overlap_count": len(overlaps),
            }

            return DatabaseProfile(
                database_path=self.db_path,
                database_name=self.db_name,
                checksum_sha256=checksum,
                tables=tables,
                candidate_identifiers=candidate_identifiers,
                declared_foreign_keys=all_declared_fks,
                observed_value_overlaps=overlaps,
                summary=summary,
            )
        finally:
            conn.close()
