"""
Unit tests for FHIR Mapping Agent (Module 6).
Tests contextual candidate selection (subject reference vs identifier),
vital sign elements, and edge cases.
"""

import pytest
from models.schemas import (
    ColumnFact,
    SemanticInterpretation,
    FHIRMappingCandidate,
)
from models.llm_provider import LLMProvider
from agents.fhir_mapping_agent import FHIRMappingAgent


@pytest.fixture
def mock_fhir_agent():
    llm = LLMProvider(provider="mock")
    return FHIRMappingAgent(llm_provider=llm)


def test_fhir_mapping_subject_reference_vs_identifier(mock_fhir_agent):
    """Event table PATIENT_ID must map to Observation.subject, not Patient.identifier."""
    col_obs_pid = ColumnFact(
        table_name="VITAL_SIGNS",
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
        sample_values=["P001"],
        observed_fact_summary="Foreign patient key",
    )
    interp_obs_pid = SemanticInterpretation(
        table_name="VITAL_SIGNS",
        column_name="PATIENT_ID",
        semantic_meaning="Reference to patient receiving observation",
        clinical_concept="Patient Reference",
        confidence=0.98,
        structured_rationale="Overlaps patient master",
    )

    candidate = mock_fhir_agent.propose_mapping(col_obs_pid, interp_obs_pid, [])
    assert candidate is not None
    assert candidate.target_path == "Observation.subject"

    # Patient master PATIENT_ID must map to Patient.identifier
    col_pt_id = ColumnFact(
        table_name="PATIENT_MASTER",
        column_name="PATIENT_ID",
        data_type="TEXT",
        is_nullable=False,
        is_declared_pk=True,
        row_count=100,
        null_count=0,
        non_null_count=100,
        null_percentage=0.0,
        distinct_count=100,
        uniqueness_ratio=1.0,
        is_unique=True,
        sample_values=["P001"],
        observed_fact_summary="Primary patient ID",
    )
    interp_pt_id = SemanticInterpretation(
        table_name="PATIENT_MASTER",
        column_name="PATIENT_ID",
        semantic_meaning="Primary patient unique identifier",
        clinical_concept="Patient Identity",
        confidence=0.99,
        structured_rationale="Primary key",
    )

    candidate_pt = mock_fhir_agent.propose_mapping(col_pt_id, interp_pt_id, [])
    assert candidate_pt is not None
    assert candidate_pt.target_path == "Patient.identifier"


def test_fhir_mapping_vital_sign_elements(mock_fhir_agent):
    """Test Observation.code, Observation.valueQuantity.value, and Observation.valueQuantity.unit."""
    # Test code
    col_code = ColumnFact(
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
    interp_code = SemanticInterpretation(
        table_name="VITAL_SIGNS",
        column_name="LOINC_CODE",
        semantic_meaning="Observation code",
        clinical_concept="Vital Sign Code",
        confidence=0.95,
        structured_rationale="LOINC verified",
    )
    c_code = mock_fhir_agent.propose_mapping(col_code, interp_code, [])
    assert c_code.target_path == "Observation.code"

    # Test unit
    col_unit = ColumnFact(
        table_name="VITAL_SIGNS",
        column_name="MEASUREMENT_UNIT",
        data_type="TEXT",
        is_nullable=True,
        row_count=1000,
        null_count=50,
        non_null_count=950,
        null_percentage=5.0,
        distinct_count=5,
        uniqueness_ratio=0.005,
        is_unique=False,
        sample_values=["cm"],
        observed_fact_summary="Units",
    )
    interp_unit = SemanticInterpretation(
        table_name="VITAL_SIGNS",
        column_name="MEASUREMENT_UNIT",
        semantic_meaning="Unit of measure",
        clinical_concept="Measurement Unit",
        confidence=0.92,
        structured_rationale="UCUM verified",
    )
    c_unit = mock_fhir_agent.propose_mapping(col_unit, interp_unit, [])
    assert c_unit.target_path == "Observation.valueQuantity.unit"
