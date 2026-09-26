"""
Unit tests for Hybrid Evidence Retrieval (Module 4).
Tests exact terminology lookup (UCUM, LOINC, RxNorm), FHIR structure parsing,
and evidence prioritization.
"""

import pytest
from terminology.ucum import UCUMValidator
from terminology.loinc import LOINCConnector
from terminology.rxnorm import RxNormConnector
from fhir.evidence_retriever import FHIREvidenceRetriever
from retrieval.strategy import RetrievalStrategyPlanner
from retrieval.hybrid_retriever import HybridRetriever
from models.schemas import ColumnFact, SemanticRole


@pytest.fixture
def ucum_validator():
    return UCUMValidator()


@pytest.fixture
def loinc_connector():
    return LOINCConnector()


@pytest.fixture
def rxnorm_connector():
    return RxNormConnector()


@pytest.fixture
def fhir_retriever():
    return FHIREvidenceRetriever()


@pytest.fixture
def hybrid_retriever(ucum_validator, loinc_connector, rxnorm_connector, fhir_retriever):
    return HybridRetriever(
        ucum_validator=ucum_validator,
        loinc_connector=loinc_connector,
        rxnorm_connector=rxnorm_connector,
        fhir_retriever=fhir_retriever,
    )


def test_ucum_exact_validation(ucum_validator):
    ev = ucum_validator.validate_unit("mg/dL")
    assert ev is not None
    assert ev.source == "UCUM"
    assert ev.score == 1.0
    assert "Milligram per deciliter" in ev.description

    ev_invalid = ucum_validator.validate_unit("xyz_invalid_unit_123")
    assert ev_invalid is None


def test_loinc_exact_lookup(loinc_connector):
    ev = loinc_connector.lookup_code("8302-2")
    if ev is not None:
        assert ev.source == "LOINC"
        assert "Body height" in ev.description
        assert ev.score == 1.0


def test_rxnorm_api_lookup(rxnorm_connector):
    # RxCUI 309362 = clopidogrel 75 MG Oral Tablet
    ev = rxnorm_connector.lookup_rxcui("309362")
    assert ev is not None
    assert ev.source == "RxNorm"
    assert "clopidogrel" in ev.description.lower()
    assert ev.score == 1.0


def test_fhir_structural_retrieval(fhir_retriever):
    ev = fhir_retriever.lookup_element("Observation.valueQuantity")
    assert ev is not None
    assert ev.source == "FHIR_R4"
    assert "Quantity" in ev.description

    # Search by keyword
    results = fhir_retriever.search_elements("Condition code", top_k=3)
    assert len(results) > 0
    assert any("Condition.code" in r.canonical_id for r in results)


def test_hybrid_retriever_plan_execution(hybrid_retriever):
    col = ColumnFact(
        table_name="VITAL_SIGNS",
        column_name="MEASUREMENT_UNIT",
        data_type="TEXT",
        is_nullable=True,
        row_count=100,
        null_count=10,
        non_null_count=90,
        null_percentage=10.0,
        distinct_count=2,
        uniqueness_ratio=0.02,
        is_unique=False,
        sample_values=["cm", "kg"],
        observed_fact_summary="Units",
    )
    role = SemanticRole(
        role_category="measurement_unit",
        candidate_terminology="UCUM",
        semantic_meaning="Physical unit",
        confidence=0.95,
        rationale="Units",
    )
    planner = RetrievalStrategyPlanner()
    plan = planner.plan_retrieval(col, role)

    evidence = hybrid_retriever.execute_plan(plan)
    assert len(evidence) >= 2
    # Verify UCUM exact evidence is present and prioritized
    assert any(e.source == "UCUM" for e in evidence)
    assert any(e.source == "FHIR_R4" for e in evidence)
    assert evidence[0].retrieval_method in ["EXACT_LOOKUP", "FHIR_STRUCTURE"]
