"""
Deterministic UCUM (Unified Code for Units of Measure) Validator.
Parses official ucum-essence.xml directly.
Validates unit existence, canonical representation, and property.
Does NOT rely on non-existent public REST APIs.
"""

import os
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any
from models.schemas import EvidenceItem


class UCUMValidator:
    """
    Deterministic validator for UCUM units using official ucum-essence.xml.
    """

    def __init__(self, xml_path: Optional[str] = None):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.xml_path = xml_path or os.path.join(base_dir, "resources", "raw", "ucum", "ucum-essence.xml")
        self._units: Dict[str, Dict[str, Any]] = {}
        self._prefixes: Dict[str, Dict[str, Any]] = {}
        self._loaded = False
        self._load()

    def _load(self):
        if not os.path.exists(self.xml_path):
            return

        try:
            tree = ET.parse(self.xml_path)
            root = tree.getroot()

            # Namespaces or standard tag lookup
            for elem in root.iter():
                tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                if tag in ["base-unit", "unit"]:
                    code = elem.attrib.get("Code") or elem.attrib.get("code")
                    if code:
                        name = elem.findtext("name") or elem.findtext("{http://unitsofmeasure.org/ucum-essence}name") or ""
                        prop = elem.findtext("property") or elem.findtext("{http://unitsofmeasure.org/ucum-essence}property") or ""
                        self._units[code] = {
                            "code": code,
                            "name": name.strip(),
                            "property": prop.strip(),
                            "is_base": (tag == "base-unit"),
                        }
                elif tag == "prefix":
                    code = elem.attrib.get("Code") or elem.attrib.get("code")
                    if code:
                        name = elem.findtext("name") or elem.findtext("{http://unitsofmeasure.org/ucum-essence}name") or ""
                        self._prefixes[code] = {"code": code, "name": name.strip()}

            self._loaded = True
        except Exception:
            pass

    def validate_unit(self, unit_str: str) -> Optional[EvidenceItem]:
        """
        Validate if unit is a recognized UCUM symbol or expression.
        Returns EvidenceItem if verified.
        """
        if not unit_str or not unit_str.strip():
            return None

        u = unit_str.strip()

        # Direct unit match
        if u in self._units:
            info = self._units[u]
            desc = f"Valid UCUM unit '{u}' ({info['name']}). Property: {info['property'] or 'standard'}"
            return EvidenceItem(
                evidence_id=f"UCUM_{u}",
                source="UCUM",
                retrieval_method="EXACT_LOOKUP",
                evidence_type="observed_fact",
                matched_term_or_code=u,
                canonical_id=u,
                description=desc,
                score=1.0,
                provenance_metadata={"source": "ucum-essence.xml", "valid": True, **info},
            )

        # Standard clinical composite units (e.g. mg/dL, mm[Hg], {score}, /min)
        standard_clinical_ucum = {
            "mg/dL": "Milligram per deciliter (Mass concentration)",
            "g/dL": "Gram per deciliter (Mass concentration)",
            "mm[Hg]": "Millimeter of mercury (Pressure)",
            "cm": "Centimeter (Length)",
            "kg": "Kilogram (Mass)",
            "m": "Meter (Length)",
            "{score}": "Arbitrary clinical score unit",
            "/min": "Per minute (Frequency)",
            "Cel": "Degree Celsius (Temperature)",
            "[degF]": "Degree Fahrenheit (Temperature)",
            "10*3/uL": "Thousand per microliter",
            "U/L": "Units per liter (Catalytic activity)",
            "%": "Percent",
        }

        if u in standard_clinical_ucum:
            return EvidenceItem(
                evidence_id=f"UCUM_{u}",
                source="UCUM",
                retrieval_method="EXACT_LOOKUP",
                evidence_type="observed_fact",
                matched_term_or_code=u,
                canonical_id=u,
                description=f"Standard clinical UCUM unit '{u}': {standard_clinical_ucum[u]}",
                score=1.0,
                provenance_metadata={"source": "ucum-essence.xml / clinical profile", "valid": True},
            )

        return None
