"""
Pydantic DTO Schemas for FastAPI Endpoints.
Ensures strong typing, request validation, and safe serialization.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ==============================================================================
# Project Schemas
# ==============================================================================
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    fhir_version: str = "4.0.1"


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    fhir_version: str
    status: str
    created_at: datetime
    updated_at: datetime
    database_count: int = 0
    run_count: int = 0
    mapping_count: int = 0

    class Config:
        from_attributes = True


# ==============================================================================
# Database Schemas
# ==============================================================================
class DatabaseResponse(BaseModel):
    id: str
    project_id: str
    name: str
    file_path: str
    sha256_checksum: str
    sha256: Optional[str] = None
    file_size_bytes: int
    table_count: int
    total_row_count: int
    row_count: Optional[int] = None
    status: Optional[str] = "VERIFIED"
    is_demo: bool
    created_at: datetime
    profile_summary: Optional[Dict[str, Any]] = None
    profile: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# ==============================================================================
# Analysis Run Schemas
# ==============================================================================
class AnalysisRunCreate(BaseModel):
    project_id: str
    database_id: Optional[str] = None
    database_path: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    limit: Optional[int] = None


class AnalysisRunResponse(BaseModel):
    id: str
    project_id: str
    database_id: Optional[str]
    run_id: str
    database_name: str
    status: str
    current_stage: str
    progress_percentage: float
    llm_provider: str
    llm_model: str
    total_fields: int
    accepted_count: int
    review_count: int
    unsupported_count: int
    started_at: datetime
    completed_at: Optional[datetime]
    elapsed_seconds: float
    error_message: Optional[str]

    class Config:
        from_attributes = True


# ==============================================================================
# Mapping Schemas
# ==============================================================================
class ReviewResponse(BaseModel):
    id: str
    mapping_id: str
    reviewer: str
    human_decision: str
    target_fhir_element_override: Optional[str]
    comment: Optional[str]
    reviewed_at: datetime

    class Config:
        from_attributes = True


class MappingRecordResponse(BaseModel):
    id: str
    run_id: str
    project_id: str
    database_name: str
    table_name: str
    column_name: str
    legacy_field: str
    semantic_meaning: str
    observed_facts: List[str] = []
    inferred_facts: List[str] = []
    fhir_resource: str
    fhir_element: str
    datatype: str
    cardinality: str
    binding_valueset: Optional[str]
    rationale: Optional[str]
    retrieved_evidence_summary: List[str] = []
    mapping_confidence: float
    confidence: Optional[float] = None
    evidence_strength: str
    automated_decision: str
    decision: Optional[str] = None
    hospital_source: Optional[str] = None
    rule_id: str
    decision_reason: Optional[str]
    provenance: List[str] = []
    evidence_json: Optional[Any] = None
    created_at: datetime
    latest_review: Optional[ReviewResponse] = None
    human_review: Optional[ReviewResponse] = None

    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    mapping_id: str
    reviewer: str = "Clinical Analyst"
    human_decision: str = Field(..., pattern="^(ACCEPTED|REJECTED|MODIFIED|NEEDS_INVESTIGATION)$")
    target_fhir_element_override: Optional[str] = None
    comment: Optional[str] = None


# ==============================================================================
# Dashboard & Reports Schemas
# ==============================================================================
class DashboardStatsResponse(BaseModel):
    total_projects: int
    total_databases: int
    total_runs: int
    total_fields_analyzed: int
    accepted_count: int
    review_count: int
    unsupported_count: int
    acceptance_rate: float
    review_rate: float
    unsupported_rate: float
    avg_confidence: float
    average_confidence: Optional[float] = None
    hospital_breakdown: Optional[Dict[str, Any]] = None
    fhir_resource_distribution: Dict[str, int]
    decision_distribution: Dict[str, int]
    recent_runs: List[AnalysisRunResponse]


class KnowledgeResourceItem(BaseModel):
    resource_id: str
    name: str
    version: str
    category: str
    status: str  # AVAILABLE, DEGRADED, UNAVAILABLE
    description: str
    record_count: Optional[int] = None
    checksum_sha256: Optional[str] = None
    local_path: Optional[str] = None
    details: Dict[str, Any] = {}


class SystemHealthResponse(BaseModel):
    status: str  # HEALTHY, DEGRADED, UNHEALTHY
    version: str
    fhir_version: str
    uptime_seconds: float
    database_status: str
    knowledge_resources_status: str
    llm_provider_status: str
    llm_active_provider: str
    llm_active_model: str
    total_audit_events: int
    timestamp: datetime
    components: Optional[Dict[str, Any]] = None


class AuditEventResponse(BaseModel):
    id: str
    project_id: Optional[str]
    event_type: str
    description: str
    details: Optional[Dict[str, Any]] = None
    user: str
    created_at: datetime

    class Config:
        from_attributes = True
