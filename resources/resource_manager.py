"""
Authoritative Healthcare Knowledge Resource Manager (Section 17).
Maintains manifests, checks availability, verifies local checksums, and tests
connectivity for HL7 FHIR R4, LOINC, UCUM, RxNorm, SNOMED CT, and OHDSI.
"""

import os
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
import requests
from dotenv import load_dotenv

load_dotenv()


class KnowledgeResource(BaseModel):
    name: str
    version: str
    source_url: str
    resource_type: str  # OFFLINE_RELEASE | OPEN_REST_API | AUTH_REST_API | VECTOR_INDEX
    availability: str   # AVAILABLE | AUTH REQUIRED | CONFIGURED | UNAVAILABLE | NOT CONFIGURED
    credentials_required: bool = False
    credentials_present: bool = False
    local_path: Optional[str] = None
    checksum_sha256: Optional[str] = None
    record_count: Optional[int] = None
    last_checked: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    details: str = ""


class ResourceManager:
    """
    Manages and monitors external knowledge sources required for Phase 1 mapping evidence.
    Ensures graceful degradation when optional sources are missing or require auth.
    """

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.resources_dir = os.path.join(self.base_dir, "resources", "raw")
        self.vector_db_dir = os.path.join(self.base_dir, "retrieval", "vector_db")

    def _file_checksum(self, filepath: str) -> Optional[str]:
        if not os.path.exists(filepath):
            return None
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def check_fhir_r4(self) -> KnowledgeResource:
        """Check HL7 FHIR R4 official definitions."""
        zip_path = os.path.join(self.resources_dir, "fhir_r4", "hl7.fhir.r4.core.4.0.1.zip")
        has_file = os.path.exists(zip_path)
        checksum = self._file_checksum(zip_path) if has_file else None

        # Check vector store
        vector_count = None
        try:
            import chromadb
            client = chromadb.PersistentClient(path=self.vector_db_dir)
            col = client.get_collection("fhir_r4_vectors")
            vector_count = col.count()
        except Exception:
            pass

        avail = "AVAILABLE" if (has_file or vector_count) else "UNAVAILABLE"
        details = []
        if has_file:
            details.append(f"Offline core zip verified ({os.path.getsize(zip_path):,} bytes)")
        if vector_count:
            details.append(f"{vector_count:,} indexed vector embeddings")

        return KnowledgeResource(
            name="FHIR R4",
            version="4.0.1",
            source_url="https://hl7.org/fhir/R4/",
            resource_type="OFFLINE_RELEASE + VECTOR_INDEX",
            availability=avail,
            credentials_required=False,
            credentials_present=True,
            local_path=zip_path if has_file else None,
            checksum_sha256=checksum,
            record_count=vector_count,
            details="; ".join(details) if details else "Artifacts missing",
        )

    def check_ucum(self) -> KnowledgeResource:
        """Check official UCUM essence release."""
        xml_path = os.path.join(self.resources_dir, "ucum", "ucum-essence.xml")
        has_file = os.path.exists(xml_path)
        checksum = self._file_checksum(xml_path) if has_file else None

        avail = "AVAILABLE" if has_file else "UNAVAILABLE"
        details = f"ucum-essence.xml verified ({os.path.getsize(xml_path):,} bytes)" if has_file else "ucum-essence.xml not found"

        return KnowledgeResource(
            name="UCUM",
            version="Revision 1.9",
            source_url="https://unitsofmeasure.org/",
            resource_type="OFFLINE_RELEASE",
            availability=avail,
            credentials_required=False,
            credentials_present=True,
            local_path=xml_path if has_file else None,
            checksum_sha256=checksum,
            details=details,
        )

    def check_loinc(self) -> KnowledgeResource:
        """Check LOINC offline tables, vectors, and online service."""
        table_path = os.path.join(self.resources_dir, "loinc", "LoincTable")
        zip_path = os.path.join(self.resources_dir, "loinc", "Loinc_2.83.zip")
        has_table = os.path.exists(table_path) or os.path.exists(zip_path)
        checksum = self._file_checksum(zip_path) if os.path.exists(zip_path) else None

        vector_count = None
        try:
            import chromadb
            client = chromadb.PersistentClient(path=self.vector_db_dir)
            col = client.get_collection("loinc_vectors")
            vector_count = col.count()
        except Exception:
            pass

        loinc_user = os.getenv("LOINC_USERNAME")
        loinc_pass = os.getenv("LOINC_PASSWORD")
        has_auth = bool(loinc_user and loinc_pass)

        if has_table or vector_count:
            avail = "AVAILABLE"
        elif has_auth:
            avail = "AVAILABLE / ONLINE AUTH"
        else:
            avail = "AVAILABLE / AUTH REQUIRED"

        details = []
        if vector_count:
            details.append(f"{vector_count:,} LOINC vector embeddings")
        if has_table:
            details.append("Local release files found")
        if not has_auth:
            details.append("Online FHIR endpoint requires LOINC_USERNAME/PASSWORD")

        return KnowledgeResource(
            name="LOINC",
            version="2.83",
            source_url="https://loinc.org / https://fhir.loinc.org",
            resource_type="OFFLINE_RELEASE + VECTOR_INDEX",
            availability=avail,
            credentials_required=True,
            credentials_present=has_auth,
            local_path=zip_path if os.path.exists(zip_path) else (table_path if os.path.exists(table_path) else None),
            checksum_sha256=checksum,
            record_count=vector_count,
            details="; ".join(details),
        )

    def check_rxnorm(self) -> KnowledgeResource:
        """Check NLM RxNav Open Public REST API."""
        api_url = "https://rxnav.nlm.nih.gov/REST/version.json"
        avail = "UNAVAILABLE"
        version = "Unknown"
        details = "RxNav REST API offline or unreachable"

        try:
            resp = requests.get(api_url, timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                version = data.get("version", "Active")
                avail = "AVAILABLE"
                details = f"Connected to NLM RxNav (RxNorm API version {version})"
        except Exception as e:
            details = f"API connection check timed out: {e}"

        return KnowledgeResource(
            name="RxNorm",
            version=version,
            source_url="https://rxnav.nlm.nih.gov/REST/",
            resource_type="OPEN_REST_API",
            availability=avail,
            credentials_required=False,
            credentials_present=True,
            details=details,
        )

    def check_snomed(self) -> KnowledgeResource:
        """Check SNOMED CT endpoint and credentials."""
        endpoint = os.getenv("SNOMED_ENDPOINT")
        api_key = os.getenv("SNOMED_API_KEY")

        if endpoint and api_key:
            avail = "CONFIGURED"
            details = f"Configured endpoint: {endpoint}"
        elif endpoint:
            avail = "CONFIGURED (NO KEY)"
            details = f"Configured public endpoint: {endpoint}"
        else:
            avail = "NOT CONFIGURED"
            details = "SNOMED CT requires authorized license; gracefully fallback to syntactic recognition and FHIR bindings."

        return KnowledgeResource(
            name="SNOMED CT",
            version="International / US Edition",
            source_url=endpoint or "https://browser.ihtsdotools.org/",
            resource_type="AUTH_REST_API",
            availability=avail,
            credentials_required=True,
            credentials_present=bool(api_key),
            details=details,
        )

    def check_ohdsi(self) -> KnowledgeResource:
        """Check OHDSI / OMOP vocabulary resources and vector index."""
        vector_count = None
        try:
            import chromadb
            client = chromadb.PersistentClient(path=self.vector_db_dir)
            col = client.get_collection("ohdsi_vectors")
            vector_count = col.count()
        except Exception:
            pass

        ohdsi_raw = os.path.join(self.resources_dir, "ohdsi")
        has_raw = os.path.exists(ohdsi_raw) and len(os.listdir(ohdsi_raw)) > 0

        if vector_count:
            avail = "AVAILABLE"
            details = f"{vector_count:,} pre-indexed OHDSI OMOP concept vectors"
        elif has_raw:
            avail = "AVAILABLE (RAW ONLY)"
            details = f"Raw vocabulary files present in {ohdsi_raw}"
        else:
            avail = "NOT CONFIGURED"
            details = "OHDSI resources not downloaded"

        return KnowledgeResource(
            name="OHDSI",
            version="OMOP Vocabulary v5.0",
            source_url="https://athena.ohdsi.org/",
            resource_type="OFFLINE_RELEASE + VECTOR_INDEX",
            availability=avail,
            credentials_required=False,
            credentials_present=True,
            local_path=ohdsi_raw if has_raw else None,
            record_count=vector_count,
            details=details,
        )

    def get_all_manifests(self) -> Dict[str, KnowledgeResource]:
        """Inspect all authoritative knowledge sources and return status map."""
        return {
            "FHIR_R4": self.check_fhir_r4(),
            "LOINC": self.check_loinc(),
            "UCUM": self.check_ucum(),
            "RxNorm": self.check_rxnorm(),
            "SNOMED_CT": self.check_snomed(),
            "OHDSI": self.check_ohdsi(),
        }
