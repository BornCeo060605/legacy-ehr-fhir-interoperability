"""
Unit tests for Schema Intelligence Agent (Module 2).
Tests semantic role inference, terminology candidate detection, edge cases (100% null),
and separation of observed facts from inferences.
"""

import pytest
from models.schemas import (
    ColumnFact,
    TableProfile,
    RelationshipFact,
    NumericStats,
    DateStats,
)
from models.llm_provider import LLMProvider
from agents.schema_intelligence import SchemaIntelligenceAgent


@pytest.fixture
def mock_agent():
    llm = LLMProvider(provider="mock")
    return SchemaIntelligenceAgent(llm_provider=llm)


def test_schema_intelligence_primary_identifier(mock_agent):
    col = ColumnFact(
        table_name="PATIENT_MASTER",
        column_name="PATIENT_ID",
        data_type="TEXT",
        is_nullable=False,
        is_declared_pk=True,
        row_count=354,
        null_count=0,
        non_null_count=354,
        null_percentage=0.0,
        distinct_count=354,
        uniqueness_ratio=1.0,
        is_unique=True,
        sample_values=["8d1edfd0-df60-b5c8-f51f-a2d2dc613dcc", "e10377b0-54f0-cc84-20dd-4ff3854e371c"],
        observed_fact_summary="Observed type 'TEXT'; 354 distinct values across 354 rows; Declared PK",
    )
    tbl = TableProfile(
        table_name="PATIENT_MASTER",
        row_count=354,
        column_count=5,
        columns={"PATIENT_ID": col},
        declared_primary_keys=["PATIENT_ID"],
        candidate_primary_keys=["PATIENT_ID"],
    )

    result = mock_agent.analyze_column(col, tbl, [])
    assert result.role.role_category in ["primary_identifier", "foreign_reference"]
    assert result.role.confidence >= 0.90
    assert len(result.role.observed_facts) > 0


def test_schema_intelligence_snomed_code(mock_agent):
    col = ColumnFact(
        table_name="DIAGNOSIS",
        column_name="SNOMED_CODE",
        data_type="TEXT",
        is_nullable=True,
        row_count=13953,
        null_count=0,
        non_null_count=13953,
        null_percentage=0.0,
        distinct_count=236,
        uniqueness_ratio=0.017,
        is_unique=False,
        sample_values=["224299000", "162864005", "239873007"],
        observed_fact_summary="Observed type 'TEXT'; 236 distinct codes",
    )
    tbl = TableProfile(
        table_name="DIAGNOSIS",
        row_count=13953,
        column_count=6,
        columns={"SNOMED_CODE": col},
    )

    result = mock_agent.analyze_column(col, tbl, [])
    assert result.role.role_category == "terminology_code"
    assert result.role.candidate_terminology == "SNOMED_CT"
    assert result.role.confidence >= 0.90


def test_schema_intelligence_ucum_unit(mock_agent):
    col = ColumnFact(
        table_name="VITAL_SIGNS",
        column_name="MEASUREMENT_UNIT",
        data_type="TEXT",
        is_nullable=True,
        row_count=49902,
        null_count=5439,
        non_null_count=44463,
        null_percentage=10.9,
        distinct_count=9,
        uniqueness_ratio=0.0002,
        is_unique=False,
        sample_values=["cm", "{score}", "kg", "mm[Hg]"],
        observed_fact_summary="Observed type 'TEXT'; 9 distinct units",
    )
    tbl = TableProfile(
        table_name="VITAL_SIGNS",
        row_count=49902,
        column_count=7,
        columns={"MEASUREMENT_UNIT": col},
    )

    result = mock_agent.analyze_column(col, tbl, [])
    assert result.role.role_category == "measurement_unit"
    assert result.role.candidate_terminology == "UCUM"
    assert result.role.confidence >= 0.90


def test_schema_intelligence_null_column_edge_case(mock_agent):
    """Test 100% NULL column (like ENCOUNTER.REASON in hospital_a.db)."""
    col = ColumnFact(
        table_name="ENCOUNTER",
        column_name="REASON",
        data_type="TEXT",
        is_nullable=True,
        row_count=22612,
        null_count=22612,
        non_null_count=0,
        null_percentage=100.0,
        distinct_count=0,
        uniqueness_ratio=0.0,
        is_unique=False,
        sample_values=[],
        observed_fact_summary="Observed type 'TEXT'; 100% null",
    )
    tbl = TableProfile(
        table_name="ENCOUNTER",
        row_count=22612,
        column_count=6,
        columns={"REASON": col},
    )

    result = mock_agent.analyze_column(col, tbl, [])
    assert result.role.role_category == "unknown"
    assert result.role.candidate_terminology == "UNKNOWN"
    assert result.role.confidence <= 0.20
    assert len(result.role.unknowns) > 0


def test_schema_intelligence_foreign_reference_overlap(mock_agent):
    """Test foreign reference inference backed by value overlap fact."""
    col = ColumnFact(
        table_name="DIAGNOSIS",
        column_name="PATIENT_ID",
        data_type="TEXT",
        is_nullable=True,
        row_count=13953,
        null_count=0,
        non_null_count=13953,
        null_percentage=0.0,
        distinct_count=354,
        uniqueness_ratio=0.025,
        is_unique=False,
        sample_values=["8d1edfd0-df60-b5c8-f51f-a2d2dc613dcc"],
        observed_fact_summary="Observed type 'TEXT'; 354 distinct patient keys",
    )
    tbl = TableProfile(
        table_name="DIAGNOSIS",
        row_count=13953,
        column_count=6,
        columns={"PATIENT_ID": col},
    )
    overlap = RelationshipFact(
        source_table="DIAGNOSIS",
        source_column="PATIENT_ID",
        target_table="PATIENT_MASTER",
        target_column="PATIENT_ID",
        relationship_type="VALUE_OVERLAP_INCLUSION",
        overlap_count=354,
        source_distinct_count=354,
        target_distinct_count=354,
        source_containment=1.0,
        target_containment=1.0,
        jaccard_similarity=1.0,
        observed_fact="Observed 354 overlapping distinct values between DIAGNOSIS.PATIENT_ID and PATIENT_MASTER.PATIENT_ID (100% containment)",
        inference="Values in DIAGNOSIS.PATIENT_ID are fully contained in PATIENT_MASTER.PATIENT_ID. Consistent with a foreign-key patient reference.",
    )

    result = mock_agent.analyze_column(col, tbl, [overlap])
    assert result.role.role_category in ["foreign_reference", "primary_identifier"]
    assert result.role.confidence >= 0.90
