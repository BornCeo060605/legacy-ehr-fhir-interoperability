"""
Deterministic Confidence & Evidence Engine (Module 7) and Decision Engine (Module 8).
Tracks separate scores for semantics, retrieval quality, terminology evidence, and FHIR evidence.
Calculates transparent mapping confidence and evidence strength.
Executes deterministic rule-based mapping decisions (ACCEPTED / REVIEW / UNSUPPORTED).
"""

from typing import List, Dict, Any, Optional
from models.schemas import (
    ColumnFact,
    SemanticInterpretation,
    EvidenceItem,
    FHIRMappingCandidate,
    ConfidenceBreakdown,
    MappingDecision,
)


class ConfidenceEngine:
    """
    Deterministic scoring engine that calculates transparent confidence components
    and categorizes evidence strength.
    """

    def calculate(
        self,
        column_fact: ColumnFact,
        semantic_interp: SemanticInterpretation,
        evidence: List[EvidenceItem],
        fhir_candidate: Optional[FHIRMappingCandidate],
    ) -> ConfidenceBreakdown:
        explanations: Dict[str, str] = {}

        # 1. Edge Case: 100% NULL column
        if column_fact.null_count == column_fact.row_count and column_fact.row_count > 0:
            explanations["semantic"] = "Field is 100% null; semantic confidence minimal (0.10)."
            explanations["retrieval"] = "No external queries executed due to lack of data (0.0)."
            explanations["terminology"] = "No terminology codes observable (0.0)."
            explanations["fhir"] = "No direct FHIR candidate element corroborated (0.10)."
            explanations["summary"] = "Evidence strength NONE due to complete lack of observed data."
            return ConfidenceBreakdown(
                semantic_confidence=0.10,
                retrieval_quality=0.0,
                terminology_evidence_score=0.0,
                fhir_evidence_score=0.10,
                mapping_confidence=0.10,
                evidence_strength="NONE",
                components_explanation=explanations,
            )

        # 2. Semantic Confidence
        semantic_conf = max(0.1, min(1.0, semantic_interp.confidence))
        explanations["semantic"] = f"Semantic Agent confidence: {semantic_conf:.2f} based on profiling facts."

        # 3. Terminology Evidence Score
        exact_terms = [e for e in evidence if e.retrieval_method in ["EXACT_LOOKUP", "API_CALL"]]
        vector_terms = [e for e in evidence if e.retrieval_method == "VECTOR_SEARCH"]

        tbl = column_fact.table_name.upper()
        col = column_fact.column_name.upper()
        is_identifier_or_date = "ID" in col or "DATE" in col or "NAME" in col or "GENDER" in col or "STATUS" in col

        if exact_terms:
            term_score = 1.0
            explanations["terminology"] = f"Strong exact terminology corroboration ({len(exact_terms)} exact matches)."
        elif is_identifier_or_date:
            # Identity or primitive attributes don't require terminology code lookup
            term_score = 0.90
            explanations["terminology"] = "Field is identifier/datetime/primitive; clinical vocabulary lookup not required."
        elif vector_terms and vector_terms[0].score >= 0.70:
            term_score = round(vector_terms[0].score, 2)
            explanations["terminology"] = f"Supporting vector semantic match in terminology index (similarity: {term_score:.2f})."
        else:
            term_score = 0.40
            explanations["terminology"] = "No direct or exact terminology matches found."

        # 4. FHIR Evidence Score
        fhir_ev = [e for e in evidence if e.source == "FHIR_R4"]
        if fhir_candidate and fhir_candidate.is_direct:
            if fhir_ev and any(fhir_candidate.target_path in e.canonical_id for e in fhir_ev):
                fhir_score = 1.0
                explanations["fhir"] = f"Exact match with official FHIR StructureDefinition element '{fhir_candidate.target_path}'."
            else:
                fhir_score = 0.85
                explanations["fhir"] = f"Canonical FHIR element candidate '{fhir_candidate.target_path}' corroborated."
        elif fhir_candidate:
            fhir_score = 0.50
            explanations["fhir"] = f"Indirect or fallback FHIR candidate '{fhir_candidate.target_path}'."
        else:
            fhir_score = 0.10
            explanations["fhir"] = "No valid FHIR candidate path established."

        # 5. Retrieval Quality
        retrieval_quality = 1.0 if (exact_terms or fhir_ev) else (0.80 if evidence else 0.50)
        explanations["retrieval"] = f"Retrieval coverage: {len(evidence)} total evidence items retrieved."

        # 6. Overall Mapping Confidence (Weighted deterministic blend)
        # Weights: 35% semantic, 35% fhir, 20% terminology, 10% retrieval
        mapping_conf = (
            (0.35 * semantic_conf)
            + (0.35 * fhir_score)
            + (0.20 * term_score)
            + (0.10 * retrieval_quality)
        )
        mapping_conf = round(max(0.0, min(1.0, mapping_conf)), 2)

        # 7. Evidence Strength Classification
        if (exact_terms and fhir_score >= 0.85) or (is_identifier_or_date and fhir_score >= 0.85 and semantic_conf >= 0.85):
            evidence_strength = "STRONG"
        elif fhir_score >= 0.70 and (term_score >= 0.60 or semantic_conf >= 0.75):
            evidence_strength = "MODERATE"
        elif evidence or fhir_candidate:
            evidence_strength = "WEAK"
        else:
            evidence_strength = "NONE"

        explanations["summary"] = f"Mapping confidence {mapping_conf:.2f} with {evidence_strength} evidence strength."

        return ConfidenceBreakdown(
            semantic_confidence=round(semantic_conf, 2),
            retrieval_quality=round(retrieval_quality, 2),
            terminology_evidence_score=round(term_score, 2),
            fhir_evidence_score=round(fhir_score, 2),
            mapping_confidence=mapping_conf,
            evidence_strength=evidence_strength,
            components_explanation=explanations,
        )


class DecisionEngine:
    """
    Deterministic rule engine that produces audit-traceable decisions:
    ACCEPTED, REVIEW, or UNSUPPORTED.
    """

    def decide(
        self,
        breakdown: ConfidenceBreakdown,
        fhir_candidate: Optional[FHIRMappingCandidate],
        column_fact: ColumnFact,
    ) -> MappingDecision:
        conf = breakdown.mapping_confidence
        strength = breakdown.evidence_strength

        # Rule R0: 100% Missing Data Edge Case
        if column_fact.null_count == column_fact.row_count and column_fact.row_count > 0:
            return MappingDecision(
                decision="UNSUPPORTED",
                rule_id="R0_UNPOPULATED_FIELD",
                rule_description="IF row_count > 0 AND null_count == row_count (100% missing) THEN UNSUPPORTED",
                reason=f"Column '{column_fact.column_name}' contains 100% missing values; clinical semantics unobservable.",
                confidence=conf,
                evidence_strength=strength,
            )

        # Rule R1: High Confidence & Strong Evidence -> ACCEPTED
        if conf >= 0.80 and strength == "STRONG":
            return MappingDecision(
                decision="ACCEPTED",
                rule_id="R1_STRONG_ACCEPTED",
                rule_description="IF mapping_confidence >= 0.80 AND evidence_strength == 'STRONG' THEN ACCEPTED",
                reason=f"High mapping confidence ({conf:.2f}) corroborated by strong terminology and FHIR structural evidence.",
                confidence=conf,
                evidence_strength=strength,
            )

        # Rule R2: Moderate Confidence & Moderate/Strong Evidence -> ACCEPTED
        if conf >= 0.75 and strength in ["STRONG", "MODERATE"]:
            return MappingDecision(
                decision="ACCEPTED",
                rule_id="R2_MODERATE_ACCEPTED",
                rule_description="IF mapping_confidence >= 0.75 AND evidence_strength IN ('STRONG', 'MODERATE') THEN ACCEPTED",
                reason=f"Sufficient mapping confidence ({conf:.2f}) backed by {strength} evidence strength.",
                confidence=conf,
                evidence_strength=strength,
            )

        # Rule R3: Candidate established but lower confidence or weak evidence -> REVIEW
        if conf >= 0.50 or strength in ["MODERATE", "WEAK"]:
            return MappingDecision(
                decision="REVIEW",
                rule_id="R3_MANUAL_REVIEW_REQUIRED",
                rule_description="IF mapping_confidence >= 0.50 OR evidence_strength IN ('MODERATE', 'WEAK') THEN REVIEW",
                reason=f"Candidate mapping proposed but requires clinical expert review (Confidence: {conf:.2f}, Strength: {strength}).",
                confidence=conf,
                evidence_strength=strength,
            )

        # Rule R4: Low confidence and insufficient evidence -> UNSUPPORTED
        return MappingDecision(
            decision="UNSUPPORTED",
            rule_id="R4_INSUFFICIENT_EVIDENCE",
            rule_description="IF mapping_confidence < 0.50 AND evidence_strength == 'NONE' THEN UNSUPPORTED",
            reason=f"Confidence ({conf:.2f}) below acceptance threshold with insufficient supporting evidence.",
            confidence=conf,
            evidence_strength=strength,
        )
