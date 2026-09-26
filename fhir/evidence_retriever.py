"""
FHIR R4 Structural Evidence Retriever (Section 11, Section 9C).
Extracts and indexes authoritative HL7 FHIR R4 (version 4.0.1) StructureDefinitions directly
from the official hl7.fhir.r4.core package.
Provides exact paths, data types, cardinality, short descriptions, and ValueSet bindings.
"""

import os
import json
import tarfile
import logging
from typing import Dict, Any, List, Optional
from models.schemas import EvidenceItem, FHIRMappingCandidate

logger = logging.getLogger(__name__)


class FHIREvidenceRetriever:
    """
    Retriever for official HL7 FHIR R4 StructureDefinitions and element metadata.
    """

    CORE_RESOURCES = ["Patient", "Observation", "Condition", "MedicationRequest", "Encounter"]

    def __init__(self, tgz_path: Optional[str] = None, cache_path: Optional[str] = None):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.tgz_path = tgz_path or os.path.join(base_dir, "resources", "raw", "fhir_r4", "hl7.fhir.r4.core.4.0.1.tgz")
        self.cache_path = cache_path or os.path.join(base_dir, "resources", "fhir_elements.json")
        self._elements: Dict[str, Dict[str, Any]] = {}
        self._load_structures()

    def _load_structures(self):
        """Load or extract element definitions from the core package."""
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    self._elements = json.load(f)
                return
            except Exception:
                pass

        if not os.path.exists(self.tgz_path):
            logger.warning(f"FHIR core tgz not found at {self.tgz_path}")
            return

        try:
            with tarfile.open(self.tgz_path, "r:gz") as tar:
                for res_name in self.CORE_RESOURCES:
                    member_name = f"package/StructureDefinition-{res_name}.json"
                    try:
                        f = tar.extractfile(member_name)
                        if f:
                            sd = json.load(f)
                            snapshot = sd.get("snapshot", {}).get("element", [])
                            for elem in snapshot:
                                path = elem.get("path")
                                if not path:
                                    continue

                                types = [t.get("code") for t in elem.get("type", []) if t.get("code")]
                                elem_type = types[0] if types else "Element"
                                min_card = elem.get("min", 0)
                                max_card = elem.get("max", "*")
                                card = f"{min_card}..{max_card}"
                                short = elem.get("short", "")
                                definition = elem.get("definition", "")

                                binding = elem.get("binding", {})
                                valset = binding.get("valueSet")
                                strength = binding.get("strength")

                                self._elements[path] = {
                                    "resource": res_name,
                                    "path": path,
                                    "type": elem_type,
                                    "cardinality": card,
                                    "short": short,
                                    "definition": definition,
                                    "binding_valueset": valset,
                                    "binding_strength": strength,
                                }
                    except Exception as e:
                        logger.warning(f"Error extracting {res_name} StructureDefinition: {e}")

            # Save normalized cache
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(self._elements, f, indent=2)
            logger.info(f"Indexed {len(self._elements)} FHIR R4 elements into {self.cache_path}")
        except Exception as e:
            logger.error(f"Failed to index FHIR R4 structures: {e}")

    def lookup_element(self, path: str) -> Optional[EvidenceItem]:
        """Lookup an exact FHIR element path, including choice types like Observation.valueQuantity."""
        p = path.strip()
        if p in self._elements:
            info = self._elements[p]
            desc = (
                f"Official FHIR R4 element '{p}' ({info['type']}, Cardinality: {info['cardinality']}). "
                f"Description: {info['short']}"
            )
            if info["binding_strength"]:
                desc += f" [Binding: {info['binding_strength']}]"

            return EvidenceItem(
                evidence_id=f"FHIR_R4_{p}",
                source="FHIR_R4",
                retrieval_method="FHIR_STRUCTURE",
                evidence_type="observed_fact",
                matched_term_or_code=p,
                canonical_id=p,
                description=desc,
                score=1.0,
                provenance_metadata={"source": "HL7 FHIR R4 Core 4.0.1", **info},
            )

        # Handle choice types (e.g. Observation.valueQuantity -> Observation.value[x])
        for choice_kw in ["value", "onset", "effective", "medication"]:
            needle = f".{choice_kw}"
            if needle in p:
                parts = p.split(needle, 1)
                base_path = f"{parts[0]}.{choice_kw}[x]"
                if base_path in self._elements:
                    info = self._elements[base_path]
                    desc = (
                        f"Official FHIR R4 choice element '{p}' (specialization of {base_path}, "
                        f"Cardinality: {info['cardinality']}). Description: {info['short']}"
                    )
                    return EvidenceItem(
                        evidence_id=f"FHIR_R4_{p}",
                        source="FHIR_R4",
                        retrieval_method="FHIR_STRUCTURE",
                        evidence_type="observed_fact",
                        matched_term_or_code=p,
                        canonical_id=p,
                        description=desc,
                        score=1.0,
                        provenance_metadata={"source": "HL7 FHIR R4 Core 4.0.1", "choice_base": base_path, **info},
                    )

        return None

    def search_elements(self, query: str, top_k: int = 5) -> List[EvidenceItem]:
        """
        Search for FHIR elements matching keywords.
        """
        q_tokens = query.lower().replace(".", " ").replace("_", " ").split()
        matches = []

        for path, info in self._elements.items():
            path_lower = path.lower()
            short_lower = info["short"].lower()
            score = 0
            for t in q_tokens:
                if t in path_lower:
                    score += 2
                if t in short_lower:
                    score += 1

            if score > 0:
                matches.append((score, path, info))

        matches.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, path, info in matches[:top_k]:
            results.append(
                EvidenceItem(
                    evidence_id=f"FHIR_R4_{path}",
                    source="FHIR_R4",
                    retrieval_method="FHIR_STRUCTURE",
                    evidence_type="observed_fact",
                    matched_term_or_code=path,
                    canonical_id=path,
                    description=f"FHIR R4 element '{path}' ({info['type']}, {info['cardinality']}): {info['short']}",
                    score=round(min(1.0, 0.6 + (score * 0.1)), 2),
                    provenance_metadata={"source": "HL7 FHIR R4 Core 4.0.1", **info},
                )
            )
        return results

    def get_candidate(self, path: str) -> Optional[FHIRMappingCandidate]:
        """Construct a strongly typed FHIRMappingCandidate from indexed StructureDefinition."""
        info = self._elements.get(path)
        if not info:
            return None

        return FHIRMappingCandidate(
            target_resource=info["resource"],
            target_path=info["path"],
            target_element_type=info["type"],
            cardinality=info["cardinality"],
            binding_strength=info.get("binding_strength"),
            binding_valueset=info.get("binding_valueset"),
            rationale=f"Official HL7 FHIR R4 element ({info['short']})",
            is_direct=True,
        )
