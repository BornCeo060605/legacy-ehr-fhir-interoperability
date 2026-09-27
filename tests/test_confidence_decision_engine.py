"""
Unit tests for Confidence & Evidence Engine (Module 7) and Decision Engine (Module 8).
Tests deterministic scoring, component separation, rule execution, and audit traceability.
"""

import pytest
from models.schemas import (
    ColumnFact,
    SemanticInterpretation,
    EvidenceItem,
    FHIRMappingCandidate,
    ConfidenceBreakdown,
    MappingDecision,
)
from models.confidence_decision_engine import ConfidenceEngine, DecisionEngine


@pytest.fixture
def conf_engine():
    return ConfidenceEngine()


@pytest.fixture
def decision_engine():
    return DecisionEngine()


def test_confidence_and_decision_accepted(conf_engine, decision_engine):
    """Strong evidence and verified FHIR element should yield ACCEPTED."""
    col = ColumnFact(
        table_name="VITAL_SIGNS",
        column_name="LOINC_CODE",
        data_type="TEXT",
        is_nullable=False,
        row_count=1000,
        null_count=0,
        non_null_count=1000,
        null_percentage=0.0,
        distinct_count=20,
        uniqueness_ratio=0.02,
        is_unique=False,
        sample_values=["8302-2"],
        observed_fact_summary="LOINC codes",
    )
    interp = SemanticInterpretation(
        table_name="VITAL_SIGNS",
        column_name="LOINC_CODE",
        semantic_meaning="Vital sign measurement concept",
        clinical_concept="Vital Sign Code",
        confidence=0.95,
        structured_rationale="LOINC verified",
    )
    ev_exact = EvidenceItem(
        evidence_id="LOINC_8302-2",
        source="LOINC",
        retrieval_method="EXACT_LOOKUP",
        evidence_type="observed_fact",
        matched_term_or_code="8302-2",
        canonical_id="8302-2",
        description="Official LOINC 8302-2: Body height",
        score=1.0,
    )
    ev_fhir = EvidenceItem(
        evidence_id="FHIR_Observation.code",
        source="FHIR_R4",
        retrieval_method="FHIR_STRUCTURE",
        evidence_type="observed_fact",
        matched_term_or_code="Observation.code",
        canonical_id="Observation.code",
        description="Observation.code CodeableConcept element",
        score=1.0,
    )
    candidate = FHIRMappingCandidate(
        target_resource="Observation",
        target_path="Observation.code",
        target_element_type="CodeableConcept",
        cardinality="1..1",
        rationale="Standard element for observation concept",
        is_direct=True,
    )

    breakdown = conf_engine.calculate(col, interp, [ev_exact, ev_fhir], candidate)
    assert breakdown.mapping_confidence >= 0.85
    assert breakdown.evidence_strength == "STRONG"
    assert "semantic" in breakdown.components_explanation
    assert "terminology" in breakdown.components_explanation
    assert "fhir" in breakdown.components_explanation

    decision = decision_engine.decide(breakdown, candidate, col)
    assert decision.decision == "ACCEPTED"
    assert "R1" in decision.rule_id or "R2" in decision.rule_id


def test_decision_null_field_unsupported(conf_engine, decision_engine):
    """100% null field must yield UNSUPPORTED via rule R0."""
    col = ColumnFact(
        table_name="ENCOUNTER",
        column_name="REASON",
        data_type="TEXT",
        is_nullable=True,
        row_count=1000,
        null_count=1000,
        non_null_count=0,
        null_percentage=100.0,
        distinct_count=0,
        uniqueness_ratio=0.0,
        is_unique=False,
        sample_values=[],
        observed_fact_summary="100% null",
    )
    interp = SemanticInterpretation(
        table_name="ENCOUNTER",
        column_name="REASON",
        semantic_meaning="Unpopulated attribute",
        clinical_concept="Unpopulated",
        confidence=0.10,
        structured_rationale="Null",
    )
    candidate = FHIRMappingCandidate(
        target_resource="Encounter",
        target_path="Encounter.reasonCode",
        target_element_type="CodeableConcept",
        cardinality="0..*",
        rationale="Unpopulated",
        is_direct=False,
    )

    breakdown = conf_engine.calculate(col, interp, [], candidate)
    assert breakdown.mapping_confidence <= 0.20
    assert breakdown.evidence_strength == "NONE"

    decision = decision_engine.decide(breakdown, candidate, col)
    assert decision.decision == "UNSUPPORTED"
    assert decision.rule_id == "R0_UNPOPULATED_FIELD"


def test_decision_weak_evidence_review(conf_engine, decision_engine):
    """Borderline confidence or weak evidence must trigger REVIEW."""
    col = ColumnFact(
        table_name="UNKNOWN_TABLE",
        column_name="ATTR_X",
        data_type="TEXT",
        is_nullable=True,
        row_count=100,
        null_count=20,
        non_null_count=80,
        null_percentage=20.0,
        distinct_count=10,
        uniqueness_ratio=0.125,
        is_unique=False,
        sample_values=["VAL1", "VAL2"],
        observed_fact_summary="Generic attribute",
    )
    interp = SemanticInterpretation(
        table_name="UNKNOWN_TABLE",
        column_name="ATTR_X",
        semantic_meaning="Uncertain attribute",
        clinical_concept="Ambiguous",
        confidence=0.55,
        structured_rationale="Vector match only",
    )
    ev_vec = EvidenceItem(
        evidence_id="VEC_1",
        source="OHDSI",
        retrieval_method="VECTOR_SEARCH",
        evidence_type="context",
        matched_term_or_code="VAL1",
        canonical_id="VAL1",
        description="Weak semantic match",
        score=0.60,
    )
    candidate = FHIRMappingCandidate(
        target_resource="Observation",
        target_path="Observation.component",
        target_element_type="Element",
        cardinality="0..*",
        rationale="Uncertain match",
        is_direct=False,
    )

    breakdown = conf_engine.calculate(col, interp, [ev_vec], candidate)
    decision = decision_engine.decide(breakdown, candidate, col)
    assert decision.decision == "REVIEW"
    assert "REVIEW" in decision.rule_id
