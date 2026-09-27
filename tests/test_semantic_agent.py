"""
Unit tests for Semantic Agent (Module 5).
Tests semantic reasoning over supplied evidence, conflict detection, and edge cases.
"""

import pytest
from models.schemas import (
    ColumnFact,
    SemanticRole,
    RetrievalPlan,
    EvidenceItem,
    SemanticInterpretation,
)
from models.llm_provider import LLMProvider
from agents.semantic_agent import SemanticAgent


@pytest.fixture
def mock_semantic_agent():
    llm = LLMProvider(provider="mock")
    return SemanticAgent(llm_provider=llm)


def test_semantic_agent_exact_evidence(mock_semantic_agent):
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
        observed_fact_summary="Observed 20 distinct codes",
    )
    role = SemanticRole(
        role_category="terminology_code",
        candidate_terminology="LOINC",
        semantic_meaning="Vital sign measurement code",
        confidence=0.95,
        rationale="LOINC pattern",
    )
    plan = RetrievalPlan(
        table_name="VITAL_SIGNS",
        column_name="LOINC_CODE",
        included_sources=["LOINC", "FHIR_R4"],
        excluded_sources=["UCUM"],
        queries=[],
        justification="Test",
    )
    ev = EvidenceItem(
        evidence_id="LOINC_8302-2",
        source="LOINC",
        retrieval_method="EXACT_LOOKUP",
        evidence_type="observed_fact",
        matched_term_or_code="8302-2",
        canonical_id="8302-2",
        description="Official LOINC concept 8302-2: 'Body height'",
        score=1.0,
    )

    interp = mock_semantic_agent.interpret(col, role, plan, [ev], [])
    assert isinstance(interp, SemanticInterpretation)
    assert interp.confidence >= 0.85
    assert len(interp.observed_facts) > 0


def test_semantic_agent_null_edge_case(mock_semantic_agent):
    col = ColumnFact(
        table_name="ENCOUNTER",
        column_name="REASON",
        data_type="TEXT",
        is_nullable=True,
        row_count=500,
        null_count=500,
        non_null_count=0,
        null_percentage=100.0,
        distinct_count=0,
        uniqueness_ratio=0.0,
        is_unique=False,
        sample_values=[],
        observed_fact_summary="100% null",
    )
    role = SemanticRole(
        role_category="unknown",
        candidate_terminology="UNKNOWN",
        semantic_meaning="Unpopulated field",
        confidence=0.1,
        rationale="Null",
    )
    plan = RetrievalPlan(
        table_name="ENCOUNTER",
        column_name="REASON",
        included_sources=["FHIR_R4"],
        excluded_sources=["LOINC"],
        queries=[],
        justification="Test",
    )

    interp = mock_semantic_agent.interpret(col, role, plan, [], [])
    assert interp.confidence <= 0.20
    assert len(interp.uncertainties) > 0
    assert "100% missing" in interp.structured_rationale
