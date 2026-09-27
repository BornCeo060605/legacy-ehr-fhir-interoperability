"""
Semantic Agent (Module 5).
Reasons strictly over supplied evidence (profiling facts, cross-table relationships,
and retrieved authoritative evidence).
Synthesizes clinical semantics, identifies conflicts, and calculates semantic confidence.
Does NOT perform independent searches.
Does NOT expose private chain-of-thought.
"""

import json
import logging
from typing import List, Dict, Any, Optional

from models.schemas import (
    ColumnFact,
    SemanticRole,
    RetrievalPlan,
    EvidenceItem,
    RelationshipFact,
    SemanticInterpretation,
)
from models.llm_provider import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are a Healthcare Semantic Interpretation Agent.
Your job is to reason ONLY over the supplied database profiling facts and external authoritative evidence to determine the precise semantic meaning of a legacy database field.

CRITICAL RULES:
1. Reason ONLY using the supplied evidence items. Do NOT assume facts not present in the input.
2. Evidence Priority Hierarchy:
   - Priority 1: Direct database profiling facts (exact types, values, null statistics).
   - Priority 2: Cross-table relationship overlaps (containment, linkage).
   - Priority 3: Exact terminology evidence (exact LOINC, UCUM, RxNorm lookups).
   - Priority 4: FHIR R4 structural definitions and bindings.
   - Priority 5: Semantic vector matches (supporting context only; not conclusive proof).
3. Identify any conflicting evidence (e.g., column named DATE but values are numbers).
4. Identify uncertainties (e.g., 40% missing codes, ambiguous acronyms).
5. Never expose raw private chain-of-thought; produce concise structured rationale.

You MUST respond strictly with a valid JSON object matching this schema:
{
  "semantic_meaning": "<concise description of legacy field>",
  "clinical_concept": "<e.g. Condition Diagnosis, Vital Sign Quantitative Measurement, Patient Demographics, Medication Order>",
  "terminology_interpretation": "<e.g. Verified LOINC 8302-2 (Body height) | Verified UCUM unit | Uncoded>",
  "observed_facts": ["<fact 1>", "<fact 2>"],
  "inferred_facts": ["<inference 1>", "<inference 2>"],
  "conflicting_evidence": ["<conflict 1>"],
  "uncertainties": ["<uncertainty 1>"],
  "confidence": <float 0.0 to 1.0>,
  "structured_rationale": "<concise evidence-based rationale>"
}"""


class SemanticAgent:
    """
    Semantic Agent reasoning over structured evidence.
    """

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm = llm_provider or LLMProvider()

    def _build_evidence_prompt(
        self,
        column_fact: ColumnFact,
        role: SemanticRole,
        plan: RetrievalPlan,
        evidence: List[EvidenceItem],
        overlaps: List[RelationshipFact],
    ) -> str:
        lines = [
            f"FIELD UNDER ANALYSIS: {column_fact.table_name}.{column_fact.column_name}",
            f"PROPOSED SEMANTIC ROLE: {role.role_category} (Terminology: {role.candidate_terminology})",
            f"INITIAL CONFIDENCE: {role.confidence:.2f}",
            f"PROFILING SUMMARY: {column_fact.observed_fact_summary}",
        ]

        if column_fact.sample_values:
            lines.append(f"SAMPLE VALUES: {column_fact.sample_values[:5]}")
        else:
            lines.append("SAMPLE VALUES: [NONE - 100% NULL]")

        # Cross table linkage
        rel_overlaps = [
            o for o in overlaps
            if (o.source_table == column_fact.table_name and o.source_column == column_fact.column_name)
            or (o.target_table == column_fact.table_name and o.target_column == column_fact.column_name)
        ]
        if rel_overlaps:
            lines.append("\nRELATIONAL LINKAGE FACTS:")
            for o in rel_overlaps[:3]:
                lines.append(f"  - {o.observed_fact} -> {o.inference}")

        # Retrieved external evidence
        lines.append("\nRETRIEVED EXTERNAL EVIDENCE:")
        if evidence:
            for i, ev in enumerate(evidence[:8], 1):
                lines.append(
                    f"  [{i}] Source={ev.source} | Method={ev.retrieval_method} | Score={ev.score} | "
                    f"Term={ev.matched_term_or_code} -> {ev.description}"
                )
        else:
            lines.append("  (No external evidence retrieved or all external sources excluded)")

        # Excluded sources
        if plan.excluded_sources:
            lines.append("\nEXCLUDED SOURCES & JUSTIFICATIONS:")
            for s, r in list(plan.exclusion_reasons.items())[:4]:
                lines.append(f"  - Excluded {s}: {r}")

        return "\n".join(lines)

    def interpret(
        self,
        column_fact: ColumnFact,
        role: SemanticRole,
        plan: RetrievalPlan,
        evidence: List[EvidenceItem],
        overlaps: List[RelationshipFact],
    ) -> SemanticInterpretation:
        """
        Synthesize supplied evidence into a structured semantic interpretation.
        """
        # Edge case: 100% NULL column
        if column_fact.null_count == column_fact.row_count and column_fact.row_count > 0:
            return SemanticInterpretation(
                table_name=column_fact.table_name,
                column_name=column_fact.column_name,
                semantic_meaning=f"Completely unpopulated legacy field '{column_fact.column_name}'",
                clinical_concept="Unpopulated Clinical Attribute",
                terminology_interpretation="None (No values observed)",
                observed_facts=[f"Column has 0 non-null values across {column_fact.row_count} rows."],
                inferred_facts=[],
                conflicting_evidence=[],
                uncertainties=["Clinical intent cannot be validated without empirical values."],
                confidence=0.10,
                structured_rationale="Field is 100% missing in legacy database; no terminology evidence can be corroborated.",
            )

        prompt = self._build_evidence_prompt(column_fact, role, plan, evidence, overlaps)
        resp: LLMResponse = self.llm.generate(prompt=prompt, system_prompt=SYSTEM_PROMPT, json_mode=True)

        if resp.success and resp.parsed_json:
            p = resp.parsed_json
            return SemanticInterpretation(
                table_name=column_fact.table_name,
                column_name=column_fact.column_name,
                semantic_meaning=p.get("semantic_meaning", role.semantic_meaning),
                clinical_concept=p.get("clinical_concept", "Clinical Concept"),
                terminology_interpretation=p.get("terminology_interpretation"),
                observed_facts=p.get("observed_facts", [column_fact.observed_fact_summary]),
                inferred_facts=p.get("inferred_facts", []),
                conflicting_evidence=p.get("conflicting_evidence", []),
                uncertainties=p.get("uncertainties", []),
                confidence=float(p.get("confidence", 0.7)),
                structured_rationale=p.get("structured_rationale", "Synthesized from evidence items."),
            )

        # Deterministic fallback
        return self._fallback_interpretation(column_fact, role, evidence, overlaps)

    def _fallback_interpretation(
        self,
        column_fact: ColumnFact,
        role: SemanticRole,
        evidence: List[EvidenceItem],
        overlaps: List[RelationshipFact],
    ) -> SemanticInterpretation:
        exact_matches = [e for e in evidence if e.retrieval_method in ["EXACT_LOOKUP", "API_CALL"]]
        term_desc = exact_matches[0].description if exact_matches else None
        conf = 0.95 if exact_matches else (0.85 if evidence else 0.70)

        return SemanticInterpretation(
            table_name=column_fact.table_name,
            column_name=column_fact.column_name,
            semantic_meaning=role.semantic_meaning,
            clinical_concept=role.target_concept_type or "Clinical Entity",
            terminology_interpretation=term_desc,
            observed_facts=[column_fact.observed_fact_summary] + [e.description for e in exact_matches[:2]],
            inferred_facts=role.inferred_facts,
            conflicting_evidence=[],
            uncertainties=role.unknowns,
            confidence=conf,
            structured_rationale=f"Evidence corroborated via {len(exact_matches)} exact matches and {len(evidence)} total items.",
        )
