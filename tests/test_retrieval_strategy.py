"""
Unit tests for Deterministic Retrieval Strategy Planner (Module 3).
Verifies correct source inclusion, exclusion reasoning, and query formulation across roles.
"""

import pytest
from models.schemas import ColumnFact, SemanticRole
from retrieval.strategy import RetrievalStrategyPlanner


@pytest.fixture
def planner():
    return RetrievalStrategyPlanner()


def test_plan_retrieval_measurement_unit(planner):
    col = ColumnFact(
        table_name="VITAL_SIGNS",
        column_name="MEASUREMENT_UNIT",
        data_type="TEXT",
        is_nullable=True,
        row_count=100,
        null_count=10,
        non_null_count=90,
        null_percentage=10.0,
        distinct_count=5,
        uniqueness_ratio=0.05,
        is_unique=False,
        sample_values=["mg/dL", "cm", "kg"],
        observed_fact_summary="Units of measure",
    )
    role = SemanticRole(
        role_category="measurement_unit",
        candidate_terminology="UCUM",
        semantic_meaning="Physical measurement unit",
        confidence=0.92,
        rationale="Unit tokens",
    )

    plan = planner.plan_retrieval(col, role)
    assert "UCUM" in plan.included_sources
    assert "FHIR_R4" in plan.included_sources
    assert "LOINC" in plan.excluded_sources
    assert "RxNorm" in plan.excluded_sources
    assert len(plan.exclusion_reasons["LOINC"]) > 0
    assert any(q.source == "UCUM" and q.query_type == "EXACT_UNIT" for q in plan.queries)


def test_plan_retrieval_loinc_code(planner):
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
        sample_values=["8302-2", "29463-7"],
        observed_fact_summary="LOINC codes",
    )
    role = SemanticRole(
        role_category="terminology_code",
        candidate_terminology="LOINC",
        semantic_meaning="Vital sign measurement code",
        confidence=0.95,
        rationale="LOINC format",
    )

    plan = planner.plan_retrieval(col, role)
    assert "LOINC" in plan.included_sources
    assert "FHIR_R4" in plan.included_sources
    assert "UCUM" in plan.excluded_sources
    assert "RxNorm" in plan.excluded_sources
    assert any(q.source == "LOINC" and q.query_type == "EXACT_CODE" for q in plan.queries)


def test_plan_retrieval_rxnorm_code(planner):
    col = ColumnFact(
        table_name="MEDICATION",
        column_name="RXNORM_CODE",
        data_type="TEXT",
        is_nullable=True,
        row_count=500,
        null_count=50,
        non_null_count=450,
        null_percentage=10.0,
        distinct_count=50,
        uniqueness_ratio=0.1,
        is_unique=False,
        sample_values=["309362", "312961"],
        observed_fact_summary="RxNorm codes",
    )
    role = SemanticRole(
        role_category="terminology_code",
        candidate_terminology="RxNorm",
        semantic_meaning="Medication RxCUI",
        confidence=0.95,
        rationale="RxNorm format",
    )

    plan = planner.plan_retrieval(col, role)
    assert "RxNorm" in plan.included_sources
    assert "FHIR_R4" in plan.included_sources
    assert "UCUM" in plan.excluded_sources
    assert any(q.source == "RxNorm" and q.query_type == "API_LOOKUP" for q in plan.queries)


def test_plan_retrieval_foreign_reference(planner):
    col = ColumnFact(
        table_name="DIAGNOSIS",
        column_name="PATIENT_ID",
        data_type="TEXT",
        is_nullable=False,
        row_count=1000,
        null_count=0,
        non_null_count=1000,
        null_percentage=0.0,
        distinct_count=100,
        uniqueness_ratio=0.1,
        is_unique=False,
        sample_values=["P001", "P002"],
        observed_fact_summary="Patient IDs",
    )
    role = SemanticRole(
        role_category="foreign_reference",
        candidate_terminology="FHIR_CORE",
        semantic_meaning="Patient reference",
        confidence=0.98,
        rationale="Value overlap with patient master",
    )

    plan = planner.plan_retrieval(col, role)
    assert "FHIR_R4" in plan.included_sources
    assert "LOINC" in plan.excluded_sources
    assert "UCUM" in plan.excluded_sources
    assert "RxNorm" in plan.excluded_sources


def test_plan_retrieval_null_edge_case(planner):
    col = ColumnFact(
        table_name="ENCOUNTER",
        column_name="REASON",
        data_type="TEXT",
        is_nullable=True,
        row_count=100,
        null_count=100,
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
        semantic_meaning="100% missing attribute",
        confidence=0.1,
        rationale="Null",
    )

    plan = planner.plan_retrieval(col, role)
    assert "FHIR_R4" in plan.included_sources
    assert "LOINC" in plan.excluded_sources
    assert "100% missing" in plan.exclusion_reasons["LOINC"]
