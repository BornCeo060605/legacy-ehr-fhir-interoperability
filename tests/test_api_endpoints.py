"""
End-to-End API and Integration Tests for Phase 1 Healthcare Interoperability Application.
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db, SessionLocal, engine, Base
from app.models.entities import Project, DatabaseEntity, AnalysisRun, MappingRecord, ReviewRecord, AuditEvent
from app.services.seed_service import seed_existing_phase1_data


@pytest.fixture(scope="module")
def client():
    # Ensure tables and seed data exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_existing_phase1_data(db)
    db.close()
    
    with TestClient(app) as c:
        yield c


def test_health_endpoint(client: TestClient):
    """Test /api/health returns healthy system status and subsystem components."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["HEALTHY", "DEGRADED"]
    assert "components" in data
    assert data["components"]["database"] == "HEALTHY"
    assert data["version"] == "1.0.0"


def test_dashboard_stats_endpoint(client: TestClient):
    """Test /api/dashboard/stats returns real aggregated data from the seeded evaluations."""
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_fields_analyzed"] >= 90
    assert data["accepted_count"] > 0
    assert data["acceptance_rate"] > 0.70
    assert "hospital_breakdown" in data
    assert "fhir_resource_distribution" in data


def test_projects_crud(client: TestClient):
    """Test creating, listing, and retrieving projects."""
    # List projects
    res = client.get("/api/projects")
    assert res.status_code == 200
    projects = res.json()
    assert len(projects) >= 1

    # Create new test project
    new_proj = {
        "name": "Validation Test Project",
        "description": "Integration test scope for automated verification",
        "fhir_version": "4.0.1"
    }
    create_res = client.post("/api/projects", json=new_proj)
    assert create_res.status_code == 200
    created = create_res.json()
    assert created["name"] == "Validation Test Project"

    # Get by ID
    get_res = client.get(f"/api/projects/{created['id']}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == created["id"]


def test_databases_endpoint(client: TestClient):
    """Test /api/databases returns registered hospital SQLite databases and profiles."""
    res = client.get("/api/databases")
    assert res.status_code == 200
    dbs = res.json()
    assert len(dbs) >= 1
    
    # Check details of first database
    first_db = dbs[0]
    detail_res = client.get(f"/api/databases/{first_db['id']}")
    assert detail_res.status_code == 200
    db_data = detail_res.json()
    assert "profile" in db_data
    assert "tables" in db_data["profile"]


def test_mappings_search_and_filter(client: TestClient):
    """Test /api/mappings search, decision filtering, and detail extraction."""
    # 1. Get all mappings
    res = client.get("/api/mappings")
    assert res.status_code == 200
    all_mappings = res.json()
    assert len(all_mappings) >= 90

    # 2. Filter by decision ACCEPTED
    res_accepted = client.get("/api/mappings?decision=ACCEPTED")
    assert res_accepted.status_code == 200
    accepted = res_accepted.json()
    assert all(m["decision"] == "ACCEPTED" for m in accepted)

    # 3. Filter by search query
    res_search = client.get("/api/mappings?search=patient")
    assert res_search.status_code == 200
    searched = res_search.json()
    assert len(searched) > 0

    # 4. Get mapping detail by ID
    mapping_id = all_mappings[0]["id"]
    detail_res = client.get(f"/api/mappings/{mapping_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == mapping_id
    assert "evidence_json" in detail or "retrieved_evidence_summary" in detail


def test_review_workflow_preserves_automated_decision(client: TestClient):
    """
    CRITICAL HEALTHCARE GOVERNANCE TEST:
    A human review decision must be recorded as an explicit audit record
    and NEVER overwrite the original automated decision.
    """
    # 1. Fetch review queue
    res = client.get("/api/reviews/queue")
    assert res.status_code == 200
    queue = res.json()
    assert len(queue) > 0

    item = queue[0]
    mapping_id = item["id"]
    original_auto_decision = item["decision"]  # REVIEW

    # 2. Submit clinical sign-off
    review_payload = {
        "mapping_id": mapping_id,
        "reviewer": "Dr. Verification Specialist",
        "human_decision": "ACCEPTED",
        "comment": "Clinically confirmed as valid observation during validation test."
    }
    submit_res = client.post("/api/reviews", json=review_payload)
    assert submit_res.status_code == 200

    # 3. Verify original automated decision is unchanged in the mapping record
    mapping_check = client.get(f"/api/mappings/{mapping_id}").json()
    assert mapping_check["decision"] == original_auto_decision  # Must remain REVIEW
    assert mapping_check["human_review"] is not None
    assert mapping_check["human_review"]["human_decision"] == "ACCEPTED"
    assert mapping_check["human_review"]["reviewer"] == "Dr. Verification Specialist"


def test_reports_and_evaluation_charts(client: TestClient):
    """Test reports listing and evaluation charts gallery."""
    # List reports
    res = client.get("/api/reports")
    assert res.status_code == 200
    reports = res.json()
    assert len(reports) >= 1

    # Evaluation charts
    chart_res = client.get("/api/reports/evaluation/charts")
    assert chart_res.status_code == 200
    charts = chart_res.json()
    assert len(charts) == 10  # All 10 publication charts

    # Evaluation summary metrics
    summary_res = client.get("/api/reports/evaluation/summary")
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["total_fields_evaluated"] == 90
    assert summary["overall_strict_accuracy"] == 0.756
    assert summary["overall_normalized_accuracy"] == 0.922


def test_knowledge_resources_endpoint(client: TestClient):
    """Test /api/resources returns FHIR R4, LOINC, RxNorm, UCUM, SNOMED, OHDSI."""
    res = client.get("/api/resources")
    assert res.status_code == 200
    resources = res.json()
    assert len(resources) >= 6
    names = [r["name"] for r in resources]
    assert "FHIR R4" in names or "HL7 FHIR R4" in names
    assert "LOINC" in names
    assert "RxNorm" in names
    assert "UCUM" in names


def test_audit_trail_endpoint(client: TestClient):
    """Test /api/audit returns logged immutable governance events."""
    res = client.get("/api/audit")
    assert res.status_code == 200
    events = res.json()
    assert len(events) >= 1


def test_static_index_serving(client: TestClient):
    """Test root URL / serves the Single Page Application HTML shell."""
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "Legacy EHR → FHIR R4 Interoperability Platform" in res.text
