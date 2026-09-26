"""
SQLAlchemy ORM Entities for Industry-Grade Interoperability Platform.
Captures Projects, Databases, Analysis Runs, Mappings, Human Reviews, and Audit Events.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
    Index,
)
from sqlalchemy.orm import relationship

from app.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    fhir_version = Column(String(20), default="4.0.1")
    status = Column(String(30), default="ACTIVE")  # ACTIVE, ARCHIVED
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    databases = relationship("DatabaseEntity", back_populates="project", cascade="all, delete-orphan")
    runs = relationship("AnalysisRun", back_populates="project", cascade="all, delete-orphan")
    mappings = relationship("MappingRecord", back_populates="project", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="project", cascade="all, delete-orphan")


class DatabaseEntity(Base):
    __tablename__ = "databases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    name = Column(String(150), nullable=False)
    file_path = Column(String(500), nullable=False)
    sha256_checksum = Column(String(64), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    table_count = Column(Integer, default=0)
    total_row_count = Column(Integer, default=0)
    profile_json = Column(Text, nullable=True)  # Serialized DatabaseProfile
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="databases")
    runs = relationship("AnalysisRun", back_populates="database", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_db_project_id", "project_id"),
        Index("idx_db_checksum", "sha256_checksum"),
    )


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    database_id = Column(String(36), ForeignKey("databases.id"), nullable=True)
    run_id = Column(String(100), unique=True, nullable=False)
    database_name = Column(String(100), nullable=False)
    status = Column(String(30), default="PENDING")  # PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
    current_stage = Column(String(100), default="Initialized")
    progress_percentage = Column(Float, default=0.0)
    llm_provider = Column(String(50), default="openrouter")
    llm_model = Column(String(100), default="meta-llama/llama-3.3-70b-instruct")
    total_fields = Column(Integer, default=0)
    accepted_count = Column(Integer, default=0)
    review_count = Column(Integer, default=0)
    unsupported_count = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    elapsed_seconds = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)
    log_stream = Column(Text, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="runs")
    database = relationship("DatabaseEntity", back_populates="runs")
    mappings = relationship("MappingRecord", back_populates="run", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_run_project_id", "project_id"),
        Index("idx_run_status", "status"),
        Index("idx_run_created", "started_at"),
    )


class MappingRecord(Base):
    __tablename__ = "mapping_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_id = Column(String(36), ForeignKey("analysis_runs.id"), nullable=False)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    database_name = Column(String(100), nullable=False)
    table_name = Column(String(100), nullable=False)
    column_name = Column(String(100), nullable=False)
    legacy_field = Column(String(200), nullable=False)
    
    # Semantic Intelligence
    semantic_meaning = Column(Text, nullable=False)
    observed_facts_json = Column(Text, nullable=True)
    inferred_facts_json = Column(Text, nullable=True)
    
    # FHIR Candidate
    fhir_resource = Column(String(50), nullable=False)
    fhir_element = Column(String(150), nullable=False)
    datatype = Column(String(50), default="string")
    cardinality = Column(String(20), default="0..1")
    binding_valueset = Column(String(250), nullable=True)
    rationale = Column(Text, nullable=True)
    
    # Evidence & Decision
    retrieved_evidence_summary_json = Column(Text, nullable=True)
    mapping_confidence = Column(Float, default=0.0)
    evidence_strength = Column(String(20), default="MODERATE")  # STRONG, MODERATE, WEAK, NONE
    automated_decision = Column(String(20), default="REVIEW")  # ACCEPTED, REVIEW, UNSUPPORTED
    rule_id = Column(String(50), default="R3_MANUAL_REVIEW_REQUIRED")
    decision_reason = Column(Text, nullable=True)
    provenance_json = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    run = relationship("AnalysisRun", back_populates="mappings")
    project = relationship("Project", back_populates="mappings")
    reviews = relationship("ReviewRecord", back_populates="mapping", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_mapping_run_id", "run_id"),
        Index("idx_mapping_project_id", "project_id"),
        Index("idx_mapping_decision", "automated_decision"),
        Index("idx_mapping_confidence", "mapping_confidence"),
        Index("idx_mapping_fhir_res", "fhir_resource"),
        Index("idx_mapping_legacy_field", "legacy_field"),
    )


class ReviewRecord(Base):
    __tablename__ = "review_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    mapping_id = Column(String(36), ForeignKey("mapping_records.id"), nullable=False)
    reviewer = Column(String(100), default="Clinical Analyst")
    human_decision = Column(String(30), nullable=False)  # ACCEPTED, REJECTED, MODIFIED, NEEDS_INVESTIGATION
    target_fhir_element_override = Column(String(150), nullable=True)
    comment = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    mapping = relationship("MappingRecord", back_populates="reviews")

    __table_args__ = (
        Index("idx_review_mapping_id", "mapping_id"),
        Index("idx_review_human_decision", "human_decision"),
    )


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True)
    event_type = Column(String(50), nullable=False)  # PROJECT_CREATED, DB_UPLOADED, RUN_STARTED, MAPPING_ACCEPTED, REVIEW_RECORDED, etc.
    description = Column(Text, nullable=False)
    details_json = Column(Text, nullable=True)
    user = Column(String(100), default="system")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    project = relationship("Project", back_populates="audit_events")

    __table_args__ = (
        Index("idx_audit_project_id", "project_id"),
        Index("idx_audit_event_type", "event_type"),
        Index("idx_audit_created_at", "created_at"),
    )
