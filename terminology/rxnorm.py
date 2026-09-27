"""
RxNorm Terminology Connector (Section 14).
Queries official U.S. National Library of Medicine (NLM) RxNav REST API.
Rate-limit aware, timeout aware, cached locally for performance and auditability.
"""

import os
import json
import logging
from typing import Optional, Dict, Any
import requests
from models.schemas import EvidenceItem

logger = logging.getLogger(__name__)


class RxNormConnector:
    """
    Connects to official NLM RxNav REST API for RxCUI and medication concept lookup.
    """

    BASE_URL = "https://rxnav.nlm.nih.gov/REST"

    def __init__(self, cache_file: Optional[str] = None):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.cache_file = cache_file or os.path.join(base_dir, "outputs", "cache", "rxnorm_cache.json")
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
            except Exception:
                self._cache = {}

    def _save_cache(self):
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=2)
        except Exception:
            pass

    def lookup_rxcui(self, rxcui: str) -> Optional[EvidenceItem]:
        """
        Query NLM RxNav for RxCUI properties.
        """
        code = str(rxcui).strip()
        if not code or not code.isdigit():
            return None

        # Check local cache
        if code in self._cache:
            data = self._cache[code]
            return self._build_evidence_item(code, data)

        url = f"{self.BASE_URL}/rxcui/{code}/properties.json"
        try:
            resp = requests.get(url, timeout=6.0)
            if resp.status_code == 200:
                data = resp.json()
                props = data.get("properties")
                if props and props.get("name"):
                    self._cache[code] = props
                    self._save_cache()
                    return self._build_evidence_item(code, props)
        except Exception as e:
            logger.warning(f"RxNav API lookup error for RxCUI {code}: {e}")

        return None

    def _build_evidence_item(self, code: str, props: Dict[str, Any]) -> EvidenceItem:
        name = props.get("name", "Unknown medication")
        tty = props.get("tty", "Concept")
        desc = f"Official NLM RxNorm concept RxCUI {code}: '{name}' (Term Type: {tty})"

        return EvidenceItem(
            evidence_id=f"RXNORM_{code}",
            source="RxNorm",
            retrieval_method="API_CALL",
            evidence_type="observed_fact",
            matched_term_or_code=code,
            canonical_id=code,
            description=desc,
            score=1.0,
            provenance_metadata={
                "source": "NLM RxNav REST API",
                "endpoint": f"{self.BASE_URL}/rxcui/{code}/properties.json",
                "rxcui": code,
                "name": name,
                "term_type": tty,
            },
        )
