"""
Domain models and schema definitions for Legacy EHR -> FHIR R4 Interoperability Pipeline.
All pipeline data contracts are strictly typed using Pydantic v2.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# MODULE 1: SCHEMA PROFILER SCHEMAS
# ============================================================================

class NumericStats(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None
    mean: Optional[float] = None
    is_integer: bool = False


class DateStats(BaseModel):
    min_date: Optional[str] = None
    max_date: Optional[str] = None
    likely_format: Optional[str] = None


class ColumnFact(BaseModel):
    table_name: str
    column_name: str
    data_type: str
    is_nullable: bool
    is_declared_pk: bool = False
    row_count: int
    null_count: int
    non_null_count: int
    null_percentage: float
    distinct_count: int
    uniqueness_ratio: float
    is_unique: bool
    sample_values: List[str] = Field(default_factory=list)
    numeric_stats: Optional[NumericStats] = None
    date_stats: Optional[DateStats] = None
    top_frequent_values: Dict[str, int] = Field(default_factory=dict)
    observed_fact_summary: str


class RelationshipFact(BaseModel):
    source_table: str
    source_column: str
    target_table: str
    target_column: str
    relationship_type: Literal["DECLARED_FOREIGN_KEY", "VALUE_OVERLAP_INCLUSION", "VALUE_OVERLAP_PARTIAL"]
    overlap_count: int
    source_distinct_count: int
    target_distinct_count: int
    source_containment: float
    target_containment: float
    jaccard_similarity: float
    observed_fact: str
    inference: str


class TableProfile(BaseModel):
    table_name: str
    row_count: int
    column_count: int
    columns: Dict[str, ColumnFact]
    declared_primary_keys: List[str] = Field(default_factory=list)
    declared_foreign_keys: List[Dict[str, Any]] = Field(default_factory=list)
    candidate_primary_keys: List[str] = Field(default_factory=list)


class DatabaseProfile(BaseModel):
    database_path: str
    database_name: str
    checksum_sha256: str
    profiling_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    tables: Dict[str, TableProfile]
    candidate_identifiers: List[Dict[str, Any]] = Field(default_factory=list)
    declared_foreign_keys: List[Dict[str, Any]] = Field(default_factory=list)
    observed_value_overlaps: List[RelationshipFact] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# MODULE 2: SCHEMA INTELLIGENCE AGENT SCHEMAS
# ============================================================================

class SemanticRole(BaseModel):
    role_category: Literal[
        "primary_identifier",
        "foreign_reference",
        "terminology_code",
        "concept_display",
        "measurement_value",
        "measurement_unit",
        "timestamp_datetime",
        "demographic_attribute",
        "status_code",
        "free_text_note",
        "administrative_attribute",
        "unknown"
    ]
    target_concept_type: Optional[str] = None
    candidate_terminology: Optional[Literal["SNOMED_CT", "LOINC", "RxNorm", "UCUM", "FHIR_CORE", "UNKNOWN"]] = None
    semantic_meaning: str
    confidence: float
    observed_facts: List[str] = Field(default_factory=list)
    inferred_facts: List[str] = Field(default_factory=list)
    unknowns: List[str] = Field(default_factory=list)
    rationale: str


class SchemaIntelligenceResult(BaseModel):
    table_name: str
    column_name: str
    role: SemanticRole
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ============================================================================
# MODULE 3: RETRIEVAL STRATEGY SCHEMAS
# ============================================================================

class RetrievalQuery(BaseModel):
    source: Literal["FHIR_R4", "LOINC", "UCUM", "RxNorm", "SNOMED_CT", "OHDSI"]
    query_type: Literal["EXACT_CODE", "EXACT_UNIT", "STRUCTURAL_SEARCH", "VECTOR_SEMANTIC", "API_LOOKUP"]
    query_string: str
    priority: int = 1
    reasoning: str


class RetrievalPlan(BaseModel):
    table_name: str
    column_name: str
    included_sources: List[str] = Field(default_factory=list)
    excluded_sources: List[str] = Field(default_factory=list)
    exclusion_reasons: Dict[str, str] = Field(default_factory=dict)
    queries: List[RetrievalQuery] = Field(default_factory=list)
    justification: str


# ============================================================================
# MODULE 4: HYBRID EVIDENCE SCHEMAS
# ============================================================================

class EvidenceItem(BaseModel):
    evidence_id: str
    source: Literal["FHIR_R4", "LOINC", "UCUM", "RxNorm", "SNOMED_CT", "OHDSI", "SCHEMA_OBSERVATION"]
    retrieval_method: Literal["EXACT_LOOKUP", "FHIR_STRUCTURE", "VECTOR_SEARCH", "API_CALL", "DIRECT_PROFILING"]
    evidence_type: Literal["observed_fact", "inference", "conflict", "context"]
    matched_term_or_code: str
    canonical_id: Optional[str] = None
    description: str
    score: float = 1.0  # 1.0 for exact, similarity score for vector
    provenance_metadata: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# MODULE 5 & 6: SEMANTIC & FHIR MAPPING SCHEMAS
# ============================================================================

class SemanticInterpretation(BaseModel):
    table_name: str
    column_name: str
    semantic_meaning: str
    clinical_concept: str
    terminology_interpretation: Optional[str] = None
    observed_facts: List[str] = Field(default_factory=list)
    inferred_facts: List[str] = Field(default_factory=list)
    conflicting_evidence: List[str] = Field(default_factory=list)
    uncertainties: List[str] = Field(default_factory=list)
    confidence: float
    structured_rationale: str


class FHIRMappingCandidate(BaseModel):
    target_resource: str
    target_path: str
    target_element_type: str
    cardinality: Optional[str] = None
    binding_strength: Optional[str] = None
    binding_valueset: Optional[str] = None
    rationale: str
    is_direct: bool = True
    alternative_candidates: List[str] = Field(default_factory=list)


# ============================================================================
# MODULE 7 & 8: CONFIDENCE, DECISION & REPORT SCHEMAS
# ============================================================================

class ConfidenceBreakdown(BaseModel):
    semantic_confidence: float
    retrieval_quality: float
    terminology_evidence_score: float
    fhir_evidence_score: float
    mapping_confidence: float
    evidence_strength: Literal["STRONG", "MODERATE", "WEAK", "NONE"]
    components_explanation: Dict[str, str] = Field(default_factory=dict)


class MappingDecision(BaseModel):
    decision: Literal["ACCEPTED", "REVIEW", "UNSUPPORTED"]
    rule_id: str
    rule_description: str
    reason: str
    confidence: float
    evidence_strength: Literal["STRONG", "MODERATE", "WEAK", "NONE"]


class MappingReportItem(BaseModel):
    legacy_field: str
    table_name: str
    column_name: str
    semantic_meaning: str
    observed_facts: List[str]
    inferred_facts: List[str]
    retrieved_evidence_summary: List[str]
    fhir_candidate: Optional[FHIRMappingCandidate] = None
    confidence_breakdown: ConfidenceBreakdown
    decision: MappingDecision
    provenance: List[str]
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class Phase1AuditReport(BaseModel):
    run_id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    database_path: str
    database_name: str
    database_checksum_sha256: str
    llm_provider: str
    llm_model: str
    total_fields: int
    accepted_count: int
    review_count: int
    unsupported_count: int
    field_reports: List[MappingReportItem]
    knowledge_sources_manifest: Dict[str, Any] = Field(default_factory=dict)
