"""
Mapping Management Service.
Handles querying, filtering, search, and detailed inspection of Phase 1 mapping records.
"""

import json
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc

from app.models.entities import MappingRecord, ReviewRecord
from app.schemas.api_schemas import MappingRecordResponse, ReviewResponse


class MappingService:

    @staticmethod
    def _to_response(rec: MappingRecord) -> MappingRecordResponse:
        observed = json.loads(rec.observed_facts_json) if rec.observed_facts_json else []
        inferred = json.loads(rec.inferred_facts_json) if rec.inferred_facts_json else []
        evidence = json.loads(rec.retrieved_evidence_summary_json) if rec.retrieved_evidence_summary_json else []
        provenance = json.loads(rec.provenance_json) if rec.provenance_json else []

        latest_rev = None
        if rec.reviews:
            # Sort by reviewed_at desc
            sorted_revs = sorted(rec.reviews, key=lambda r: r.reviewed_at, reverse=True)
            top = sorted_revs[0]
            latest_rev = ReviewResponse(
                id=top.id,
                mapping_id=top.mapping_id,
                reviewer=top.reviewer,
                human_decision=top.human_decision,
                target_fhir_element_override=top.target_fhir_element_override,
                comment=top.comment,
                reviewed_at=top.reviewed_at,
            )

        return MappingRecordResponse(
            id=rec.id,
            run_id=rec.run_id,
            project_id=rec.project_id,
            database_name=rec.database_name,
            table_name=rec.table_name,
            column_name=rec.column_name,
            legacy_field=rec.legacy_field,
            semantic_meaning=rec.semantic_meaning,
            observed_facts=observed,
            inferred_facts=inferred,
            fhir_resource=rec.fhir_resource,
            fhir_element=rec.fhir_element,
            datatype=rec.datatype,
            cardinality=rec.cardinality,
            binding_valueset=rec.binding_valueset,
            rationale=rec.rationale,
            retrieved_evidence_summary=evidence,
            mapping_confidence=rec.mapping_confidence,
            confidence=rec.mapping_confidence,
            evidence_strength=rec.evidence_strength,
            automated_decision=rec.automated_decision,
            decision=rec.automated_decision,
            hospital_source=rec.database_name,
            rule_id=rec.rule_id,
            decision_reason=rec.decision_reason,
            provenance=provenance,
            evidence_json=evidence,
            created_at=rec.created_at,
            latest_review=latest_rev,
            human_review=latest_rev,
        )

    @staticmethod
    def get_mappings(
        db: Session,
        project_id: Optional[str] = None,
        run_id: Optional[str] = None,
        database_name: Optional[str] = None,
        decision: Optional[str] = None,
        resource: Optional[str] = None,
        search: Optional[str] = None,
        min_confidence: Optional[float] = None,
        max_confidence: Optional[float] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[MappingRecordResponse], int]:
        query = db.query(MappingRecord)

        if project_id:
            query = query.filter(MappingRecord.project_id == project_id)
        if run_id:
            query = query.filter(MappingRecord.run_id == run_id)
        if database_name:
            query = query.filter(MappingRecord.database_name == database_name)
        if decision:
            query = query.filter(MappingRecord.automated_decision == decision.upper())
        if resource:
            query = query.filter(MappingRecord.fhir_resource == resource)
        if min_confidence is not None:
            query = query.filter(MappingRecord.mapping_confidence >= min_confidence)
        if max_confidence is not None:
            query = query.filter(MappingRecord.mapping_confidence <= max_confidence)
        if search:
            s = f"%{search}%"
            query = query.filter(
                or_(
                    MappingRecord.legacy_field.ilike(s),
                    MappingRecord.semantic_meaning.ilike(s),
                    MappingRecord.fhir_element.ilike(s),
                    MappingRecord.fhir_resource.ilike(s),
                    MappingRecord.rule_id.ilike(s),
                )
            )

        total = query.count()
        records = query.order_by(
            MappingRecord.database_name.asc(),
            MappingRecord.table_name.asc(),
            MappingRecord.column_name.asc(),
        ).offset(skip).limit(limit).all()

        return [MappingService._to_response(r) for r in records], total

    @staticmethod
    def get_mapping(db: Session, mapping_id: str) -> Optional[MappingRecordResponse]:
        rec = db.query(MappingRecord).filter(MappingRecord.id == mapping_id).first()
        if not rec:
            return None
        return MappingService._to_response(rec)
