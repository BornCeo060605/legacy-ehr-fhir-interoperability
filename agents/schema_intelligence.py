"""
Schema Intelligence Agent (Module 2).
Uses LLM reasoning strictly over the deterministic schema profile facts.
Interprets semantic roles, candidate terminologies, and separates observed facts from inferences.
Strictly prohibited from:
  1. Directly querying the database.
  2. Accessing hidden ground truth.
  3. Performing FHIR mapping.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional

from models.schemas import (
    ColumnFact,
    TableProfile,
    RelationshipFact,
    SemanticRole,
    SchemaIntelligenceResult,
)
from models.llm_provider import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are a specialized Clinical Data Schema Intelligence Agent for healthcare legacy databases.
Your sole mission is to interpret the semantic meaning and role of a specific legacy column given ONLY deterministic profiling evidence.

RULES:
1. Rely ONLY on the observed facts and statistics provided in the prompt.
2. DO NOT perform FHIR mapping (FHIR mapping is strictly handled in later pipeline stages).
3. DO NOT invent concepts, clinical meanings, or terminologies that lack clear evidence.
4. If a field is 100% null or ambiguous, classify role as "unknown" and clearly list uncertainties.
5. Strictly distinguish:
   - observed_facts: Direct statements of database evidence (types, stats, samples, overlaps).
   - inferred_facts: Reasoning derived from evidence (e.g. format matches SNOMED CT concept ID).
   - unknowns: Gaps in evidence or ambiguities.

Valid role categories:
- primary_identifier
- foreign_reference
- terminology_code
- concept_display
- measurement_value
- measurement_unit
- timestamp_datetime
- demographic_attribute
- status_code
- free_text_note
- administrative_attribute
- unknown

Valid candidate terminologies:
- SNOMED_CT (for clinical diagnosis, findings, disorders, procedure codes)
- LOINC (for laboratory, vital signs, clinical measurements)
- RxNorm (for medication RxCUIs, NDC codes)
- UCUM (for measurement units like mg/dL, cm, kg, mm[Hg])
- FHIR_CORE (for internal references, patient IDs, encounter classes)
- UNKNOWN (when not code-based or ambiguous)

You MUST respond strictly with a valid JSON object matching this schema:
{
  "role_category": "<one of valid role categories>",
  "target_concept_type": "<e.g. Patient, Condition, Observation, Medication, Encounter>",
  "candidate_terminology": "<SNOMED_CT | LOINC | RxNorm | UCUM | FHIR_CORE | UNKNOWN>",
  "semantic_meaning": "<concise description of what this column represents>",
  "confidence": <float between 0.0 and 1.0>,
  "observed_facts": ["<fact 1>", "<fact 2>"],
  "inferred_facts": ["<inference 1>", "<inference 2>"],
  "unknowns": ["<unknown or limitation 1>"],
  "rationale": "<concise evidence-based justification>"
}"""


class SchemaIntelligenceAgent:
    """
    Schema Intelligence Agent that reasons about legacy column semantics.
    """

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm = llm_provider or LLMProvider()

    def _build_column_prompt(
        self,
        column_fact: ColumnFact,
        table_profile: TableProfile,
        relevant_overlaps: List[RelationshipFact],
    ) -> str:
        prompt_lines = [
            f"Please analyze the following legacy database column:",
            f"Table Name: {column_fact.table_name}",
            f"Column Name: {column_fact.column_name}",
            f"Declared SQLite Type: {column_fact.data_type}",
            f"Total Table Rows: {column_fact.row_count}",
            f"Null Count: {column_fact.null_count} ({column_fact.null_percentage}%)",
            f"Non-Null Count: {column_fact.non_null_count}",
            f"Distinct Count: {column_fact.distinct_count} ({column_fact.uniqueness_ratio:.1%} uniqueness)",
            f"Declared Primary Key: {'YES' if column_fact.is_declared_pk else 'NO'}",
            f"Is Unique Column: {'YES' if column_fact.is_unique else 'NO'}",
        ]

        if column_fact.sample_values:
            samples_str = ", ".join(repr(s) for s in column_fact.sample_values[:5])
            prompt_lines.append(f"Sample Values: [{samples_str}]")
        else:
            prompt_lines.append("Sample Values: NONE (Column is completely NULL)")

        if column_fact.top_frequent_values:
            freq_str = ", ".join(f"{repr(k)}: {v}" for k, v in list(column_fact.top_frequent_values.items())[:5])
            prompt_lines.append(f"Top Frequent Values: {{{freq_str}}}")

        if column_fact.numeric_stats and column_fact.numeric_stats.min is not None:
            prompt_lines.append(
                f"Numeric Characteristics: Min={column_fact.numeric_stats.min}, "
                f"Max={column_fact.numeric_stats.max}, Mean={column_fact.numeric_stats.mean}"
            )

        if column_fact.date_stats and column_fact.date_stats.likely_format:
            prompt_lines.append(
                f"Date/Time Characteristics: Detected Format={column_fact.date_stats.likely_format}, "
                f"Range=[{column_fact.date_stats.min_date} to {column_fact.date_stats.max_date}]"
            )

        # Context on other columns in this table
        sibling_cols = [c for c in table_profile.columns.keys() if c != column_fact.column_name]
        prompt_lines.append(f"Other Columns in Table '{column_fact.table_name}': {sibling_cols}")

        # Cross-table value overlap evidence
        if relevant_overlaps:
            prompt_lines.append("\nObserved Cross-Table Value Overlaps for this column:")
            for o in relevant_overlaps[:4]:
                prompt_lines.append(f"  - {o.observed_fact} -> {o.inference}")
        else:
            prompt_lines.append("\nNo cross-table value overlaps observed for this column.")

        return "\n".join(prompt_lines)

    def analyze_column(
        self,
        column_fact: ColumnFact,
        table_profile: TableProfile,
        overlaps: List[RelationshipFact],
    ) -> SchemaIntelligenceResult:
        """
        Analyze a legacy column using LLM reasoning over deterministic evidence.
        """
        # Find relevant cross-table overlaps
        rel_overlaps = [
            o for o in overlaps
            if (o.source_table == column_fact.table_name and o.source_column == column_fact.column_name)
            or (o.target_table == column_fact.table_name and o.target_column == column_fact.column_name)
        ]

        prompt = self._build_column_prompt(column_fact, table_profile, rel_overlaps)

        # Edge case: Column is 100% null
        if column_fact.null_count == column_fact.row_count and column_fact.row_count > 0:
            role = SemanticRole(
                role_category="unknown",
                target_concept_type=None,
                candidate_terminology="UNKNOWN",
                semantic_meaning=f"Unpopulated column ({column_fact.column_name}) with 100% missing values",
                confidence=0.1,
                observed_facts=[
                    f"Column '{column_fact.column_name}' has 0 non-null rows out of {column_fact.row_count} total rows."
                ],
                inferred_facts=[],
                unknowns=["True clinical or administrative semantic meaning is completely unobservable due to lack of data."],
                rationale="Deterministic rule: Field contains 100% NULL values.",
            )
            return SchemaIntelligenceResult(
                table_name=column_fact.table_name,
                column_name=column_fact.column_name,
                role=role,
            )

        resp: LLMResponse = self.llm.generate(prompt=prompt, system_prompt=SYSTEM_PROMPT, json_mode=True)

        if resp.success and resp.parsed_json:
            p = resp.parsed_json
            role = SemanticRole(
                role_category=p.get("role_category", "unknown"),
                target_concept_type=p.get("target_concept_type"),
                candidate_terminology=p.get("candidate_terminology", "UNKNOWN"),
                semantic_meaning=p.get("semantic_meaning", "Unknown semantic role"),
                confidence=float(p.get("confidence", 0.5)),
                observed_facts=p.get("observed_facts", [column_fact.observed_fact_summary]),
                inferred_facts=p.get("inferred_facts", []),
                unknowns=p.get("unknowns", []),
                rationale=p.get("rationale", "Derived from schema profiling evidence."),
            )
        else:
            # Deterministic fallback when LLM response is unavailable or unparseable
            logger.warning(f"LLM generation failed or returned invalid JSON for {column_fact.table_name}.{column_fact.column_name}: {resp.error_message}")
            role = self._deterministic_fallback_role(column_fact, rel_overlaps)

        return SchemaIntelligenceResult(
            table_name=column_fact.table_name,
            column_name=column_fact.column_name,
            role=role,
        )

    def _deterministic_fallback_role(
        self, column_fact: ColumnFact, overlaps: List[RelationshipFact]
    ) -> SemanticRole:
        """Heuristic fallback strictly derived from observable naming and profiling facts."""
        col = column_fact.column_name.upper()
        tbl = column_fact.table_name.upper()

        if column_fact.is_unique and (column_fact.is_declared_pk or "ID" in col):
            return SemanticRole(
                role_category="primary_identifier",
                target_concept_type=tbl,
                candidate_terminology="FHIR_CORE",
                semantic_meaning=f"Primary unique identifier for {tbl}",
                confidence=0.95,
                observed_facts=[column_fact.observed_fact_summary],
                inferred_facts=["100% unique key with identifier naming convention"],
                unknowns=[],
                rationale="Deterministic fallback identification based on uniqueness and ID pattern.",
            )
        elif "SNOMED" in col or (col == "PRB_CD"):
            return SemanticRole(
                role_category="terminology_code",
                target_concept_type="Condition",
                candidate_terminology="SNOMED_CT",
                semantic_meaning="Diagnosis concept code",
                confidence=0.90,
                observed_facts=[column_fact.observed_fact_summary],
                inferred_facts=["Column pattern matches SNOMED CT terminology encoding"],
                unknowns=[],
                rationale="Deterministic fallback terminology recognition.",
            )
        elif "LOINC" in col or ("MEASUREMENT" in tbl and "CODE" in col):
            return SemanticRole(
                role_category="terminology_code",
                target_concept_type="Observation",
                candidate_terminology="LOINC",
                semantic_meaning="Laboratory or vital sign concept code",
                confidence=0.90,
                observed_facts=[column_fact.observed_fact_summary],
                inferred_facts=["Matches LOINC code conventions"],
                unknowns=[],
                rationale="Deterministic fallback terminology recognition.",
            )
        elif "RXNORM" in col or ("MEDICATION" in tbl and "CODE" in col):
            return SemanticRole(
                role_category="terminology_code",
                target_concept_type="Medication",
                candidate_terminology="RxNorm",
                semantic_meaning="Medication RxCUI concept code",
                confidence=0.90,
                observed_facts=[column_fact.observed_fact_summary],
                inferred_facts=["Matches RxNorm identifier structure"],
                unknowns=[],
                rationale="Deterministic fallback terminology recognition.",
            )
        elif "UNIT" in col:
            return SemanticRole(
                role_category="measurement_unit",
                target_concept_type="Observation",
                candidate_terminology="UCUM",
                semantic_meaning="Measurement unit representation",
                confidence=0.90,
                observed_facts=[column_fact.observed_fact_summary],
                inferred_facts=["Unit tokens present in samples"],
                unknowns=[],
                rationale="Deterministic fallback unit recognition.",
            )
        elif overlaps and any("patient" in o.inference.lower() for o in overlaps):
            return SemanticRole(
                role_category="foreign_reference",
                target_concept_type="Patient",
                candidate_terminology="FHIR_CORE",
                semantic_meaning="Reference to patient master record",
                confidence=0.95,
                observed_facts=[column_fact.observed_fact_summary],
                inferred_facts=["Strong cross-table value overlap with patient master"],
                unknowns=[],
                rationale="Value overlap evidence demonstrates patient linkage.",
            )
        elif column_fact.date_stats and column_fact.date_stats.likely_format:
            return SemanticRole(
                role_category="timestamp_datetime",
                target_concept_type=tbl,
                candidate_terminology="FHIR_CORE",
                semantic_meaning="Clinical timestamp or date",
                confidence=0.85,
                observed_facts=[column_fact.observed_fact_summary],
                inferred_facts=[f"Detected date pattern {column_fact.date_stats.likely_format}"],
                unknowns=[],
                rationale="Date format detected in non-null samples.",
            )

        return SemanticRole(
            role_category="unknown",
            target_concept_type=None,
            candidate_terminology="UNKNOWN",
            semantic_meaning=f"Generic attribute in {tbl}",
            confidence=0.50,
            observed_facts=[column_fact.observed_fact_summary],
            inferred_facts=[],
            unknowns=["Ambiguous field without high-confidence terminology or identifier pattern."],
            rationale="Insufficient evidence for specific clinical semantic classification.",
        )
