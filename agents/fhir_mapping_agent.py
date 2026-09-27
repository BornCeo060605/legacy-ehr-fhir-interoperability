"""
FHIR R4 Mapping Agent (Module 6).
Proposes canonical FHIR R4 target elements based on semantic interpretations
and retrieved FHIR StructureDefinition evidence.
Strictly prohibited from inventing nonexistent FHIR paths.
"""

import json
import logging
from typing import List, Dict, Any, Optional

from models.schemas import (
    ColumnFact,
    SemanticInterpretation,
    EvidenceItem,
    FHIRMappingCandidate,
)
from models.llm_provider import LLMProvider, LLMResponse
from fhir.evidence_retriever import FHIREvidenceRetriever

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are a specialized HL7 FHIR R4 Mapping Agent.
Your job is to select the exact canonical FHIR R4 resource and element path for a legacy EHR field.

CRITICAL RULES:
1. Propose ONLY valid, official HL7 FHIR R4 element paths (e.g. Patient.identifier, Observation.subject, Condition.subject, Encounter.subject, MedicationRequest.subject, Observation.code, Observation.valueQuantity.value, Observation.valueQuantity.unit, Condition.code, MedicationRequest.medicationCodeableConcept).
2. Distinguish subject references from resource identifiers:
   - In event tables (DIAGNOSIS, ENCOUNTER, MEDICATION, VITAL_SIGNS), a patient reference column (e.g. PATIENT_ID) maps to [Resource].subject (e.g. Condition.subject, Encounter.subject, MedicationRequest.subject, Observation.subject). It NEVER maps to Patient.identifier in these event tables!
   - ONLY in the patient demographic master table (PATIENT_MASTER, PATIENTS), PATIENT_ID maps to Patient.identifier.
3. NEVER invent paths. If the field is unpopulated or evidence is insufficient, state "UNSUPPORTED" or propose with low confidence.

You MUST respond strictly with a valid JSON object matching this schema:
{
  "target_resource": "<e.g. Observation | Patient | Condition | MedicationRequest | Encounter>",
  "target_path": "<e.g. Observation.code | Patient.identifier | Observation.subject>",
  "target_element_type": "<e.g. CodeableConcept | Identifier | Reference | Quantity | dateTime | string>",
  "cardinality": "<e.g. 0..1 | 1..1 | 0..* | 1..*>",
  "binding_strength": "<required | extensible | preferred | example | null>",
  "binding_valueset": "<url or null>",
  "rationale": "<concise justification linking evidence to this FHIR element>",
  "is_direct": <true | false>,
  "alternative_candidates": ["<alternative path 1>"]
}"""


class FHIRMappingAgent:
    """
    FHIR Mapping Agent proposing authoritative FHIR R4 element mappings.
    """

    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        fhir_retriever: Optional[FHIREvidenceRetriever] = None,
    ):
        self.llm = llm_provider or LLMProvider()
        self.fhir = fhir_retriever or FHIREvidenceRetriever()

    def _build_prompt(
        self,
        column_fact: ColumnFact,
        semantic_interp: SemanticInterpretation,
        evidence: List[EvidenceItem],
    ) -> str:
        lines = [
            f"LEGACY FIELD: {column_fact.table_name}.{column_fact.column_name}",
            f"SEMANTIC MEANING: {semantic_interp.semantic_meaning}",
            f"CLINICAL CONCEPT: {semantic_interp.clinical_concept}",
            f"TERMINOLOGY INTERPRETATION: {semantic_interp.terminology_interpretation or 'None'}",
            f"SEMANTIC CONFIDENCE: {semantic_interp.confidence:.2f}",
            f"PROFILING FACTS: {column_fact.observed_fact_summary}",
        ]

        # Filter for FHIR evidence
        fhir_ev = [e for e in evidence if e.source == "FHIR_R4"]
        if fhir_ev:
            lines.append("\nCANDIDATE FHIR R4 STRUCTURAL DEFINITIONS:")
            for ev in fhir_ev[:6]:
                lines.append(f"  - Path={ev.canonical_id} | Score={ev.score} | {ev.description}")
        else:
            lines.append("\nNo specific FHIR StructureDefinition pre-retrieved.")

        return "\n".join(lines)

    def propose_mapping(
        self,
        column_fact: ColumnFact,
        semantic_interp: SemanticInterpretation,
        evidence: List[EvidenceItem],
    ) -> Optional[FHIRMappingCandidate]:
        """
        Propose a canonical FHIR R4 mapping candidate.
        """
        # Edge case: 100% NULL column
        if column_fact.null_count == column_fact.row_count and column_fact.row_count > 0:
            return FHIRMappingCandidate(
                target_resource="Encounter" if "ENC" in column_fact.table_name else "Unknown",
                target_path=f"{column_fact.table_name}.{column_fact.column_name}",
                target_element_type="Element",
                cardinality="0..1",
                rationale="Unpopulated field (100% missing); cannot establish confirmed FHIR element mapping.",
                is_direct=False,
                alternative_candidates=[],
            )

        prompt = self._build_prompt(column_fact, semantic_interp, evidence)
        resp: LLMResponse = self.llm.generate(prompt=prompt, system_prompt=SYSTEM_PROMPT, json_mode=True)

        if resp.success and resp.parsed_json:
            p = resp.parsed_json
            candidate = FHIRMappingCandidate(
                target_resource=p.get("target_resource", "Observation"),
                target_path=p.get("target_path", "Observation.code"),
                target_element_type=p.get("target_element_type", "Element"),
                cardinality=p.get("cardinality", "0..1"),
                binding_strength=p.get("binding_strength"),
                binding_valueset=p.get("binding_valueset"),
                rationale=p.get("rationale", "Selected based on clinical semantic role."),
                is_direct=p.get("is_direct", True),
                alternative_candidates=p.get("alternative_candidates", []),
            )
            return candidate

        # Deterministic fallback
        return self._deterministic_fallback_mapping(column_fact, semantic_interp)

    def _deterministic_fallback_mapping(
        self, column_fact: ColumnFact, semantic_interp: SemanticInterpretation
    ) -> FHIRMappingCandidate:
        """Deterministic mapping fallback based on verified clinical element rules."""
        tbl = column_fact.table_name.upper()
        col = column_fact.column_name.upper()

        # Subject references
        if "PATIENT" in col and tbl != "PATIENT_MASTER":
            res = "Observation" if "VITAL" in tbl else (
                "Condition" if "DIAG" in tbl else (
                    "MedicationRequest" if "MED" in tbl else (
                        "Encounter" if "ENC" in tbl else "Resource"
                    )
                )
            )
            return FHIRMappingCandidate(
                target_resource=res,
                target_path=f"{res}.subject",
                target_element_type="Reference(Patient)",
                cardinality="1..1",
                rationale=f"Foreign reference to patient master maps to {res}.subject.",
                is_direct=True,
                alternative_candidates=[f"{res}.patient"],
            )

        # Patient demographics
        if tbl == "PATIENT_MASTER":
            if "ID" in col:
                return FHIRMappingCandidate(
                    target_resource="Patient",
                    target_path="Patient.identifier",
                    target_element_type="Identifier",
                    cardinality="0..*",
                    rationale="Primary patient identifier maps to Patient.identifier.",
                    is_direct=True,
                )
            elif "BIRTH" in col:
                return FHIRMappingCandidate(
                    target_resource="Patient",
                    target_path="Patient.birthDate",
                    target_element_type="date",
                    cardinality="0..1",
                    rationale="Patient birth date maps to Patient.birthDate.",
                    is_direct=True,
                )
            elif "GENDER" in col:
                return FHIRMappingCandidate(
                    target_resource="Patient",
                    target_path="Patient.gender",
                    target_element_type="code",
                    cardinality="0..1",
                    rationale="Administrative gender maps to Patient.gender.",
                    is_direct=True,
                )
            elif "NAME" in col:
                return FHIRMappingCandidate(
                    target_resource="Patient",
                    target_path="Patient.name",
                    target_element_type="HumanName",
                    cardinality="0..*",
                    rationale="Patient name component maps to Patient.name.",
                    is_direct=True,
                )

        # Observations / Vitals
        if "VITAL" in tbl:
            if "CODE" in col:
                return FHIRMappingCandidate(
                    target_resource="Observation",
                    target_path="Observation.code",
                    target_element_type="CodeableConcept",
                    cardinality="1..1",
                    rationale="Observation concept code maps to Observation.code.",
                    is_direct=True,
                )
            elif "VALUE" in col:
                return FHIRMappingCandidate(
                    target_resource="Observation",
                    target_path="Observation.valueQuantity.value",
                    target_element_type="decimal",
                    cardinality="0..1",
                    rationale="Quantitative measurement value maps to Observation.valueQuantity.value.",
                    is_direct=True,
                )
            elif "UNIT" in col:
                return FHIRMappingCandidate(
                    target_resource="Observation",
                    target_path="Observation.valueQuantity.unit",
                    target_element_type="string",
                    cardinality="0..1",
                    rationale="Measurement unit maps to Observation.valueQuantity.unit.",
                    is_direct=True,
                )
            elif "DATE" in col:
                return FHIRMappingCandidate(
                    target_resource="Observation",
                    target_path="Observation.effectiveDateTime",
                    target_element_type="dateTime",
                    cardinality="0..1",
                    rationale="Measurement timestamp maps to Observation.effectiveDateTime.",
                    is_direct=True,
                )

        # Diagnosis / Conditions
        if "DIAG" in tbl:
            if "CODE" in col:
                return FHIRMappingCandidate(
                    target_resource="Condition",
                    target_path="Condition.code",
                    target_element_type="CodeableConcept",
                    cardinality="0..1",
                    rationale="Diagnosis code maps to Condition.code.",
                    is_direct=True,
                )
            elif "DATE" in col:
                return FHIRMappingCandidate(
                    target_resource="Condition",
                    target_path="Condition.onsetDateTime",
                    target_element_type="dateTime",
                    cardinality="0..1",
                    rationale="Condition onset timestamp maps to Condition.onsetDateTime.",
                    is_direct=True,
                )
            elif "STATUS" in col:
                return FHIRMappingCandidate(
                    target_resource="Condition",
                    target_path="Condition.clinicalStatus",
                    target_element_type="CodeableConcept",
                    cardinality="0..1",
                    rationale="Diagnosis status maps to Condition.clinicalStatus.",
                    is_direct=True,
                )

        # Medications
        if "MED" in tbl:
            if "CODE" in col:
                return FHIRMappingCandidate(
                    target_resource="MedicationRequest",
                    target_path="MedicationRequest.medicationCodeableConcept",
                    target_element_type="CodeableConcept",
                    cardinality="1..1",
                    rationale="Medication code maps to MedicationRequest.medicationCodeableConcept.",
                    is_direct=True,
                )
            elif "DATE" in col:
                return FHIRMappingCandidate(
                    target_resource="MedicationRequest",
                    target_path="MedicationRequest.authoredOn",
                    target_element_type="dateTime",
                    cardinality="0..1",
                    rationale="Prescription date maps to MedicationRequest.authoredOn.",
                    is_direct=True,
                )
            elif "STATUS" in col:
                return FHIRMappingCandidate(
                    target_resource="MedicationRequest",
                    target_path="MedicationRequest.status",
                    target_element_type="code",
                    cardinality="1..1",
                    rationale="Prescription status maps to MedicationRequest.status.",
                    is_direct=True,
                )

        # Encounters
        if "ENC" in tbl:
            if "START" in col or "END" in col or "DATE" in col:
                return FHIRMappingCandidate(
                    target_resource="Encounter",
                    target_path="Encounter.period",
                    target_element_type="Period",
                    cardinality="0..1",
                    rationale="Encounter start/end times map to Encounter.period.",
                    is_direct=True,
                )
            elif "TYPE" in col or "CLASS" in col:
                return FHIRMappingCandidate(
                    target_resource="Encounter",
                    target_path="Encounter.class",
                    target_element_type="Coding",
                    cardinality="1..1",
                    rationale="Encounter classification maps to Encounter.class.",
                    is_direct=True,
                )

        return FHIRMappingCandidate(
            target_resource=tbl.capitalize(),
            target_path=f"{tbl.capitalize()}.{col.lower()}",
            target_element_type="Element",
            cardinality="0..1",
            rationale="Heuristic fallback mapping.",
            is_direct=False,
        )
