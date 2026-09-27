"""
Human Review & Clinical Triage Service.
Allows expert clinical reviewers to record validation decisions, comments, and overrides
while strictly preserving the original automated decision for audit compliance.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.entities import ReviewRecord, MappingRecord, AuditEvent
from app.schemas.api_schemas import ReviewCreate, ReviewResponse, MappingRecordResponse
from app.services.mapping_service import MappingService


class ReviewService:

    @staticmethod
    def record_review(db: Session, data: ReviewCreate) -> Optional[ReviewResponse]:
        mapping = db.query(MappingRecord).filter(MappingRecord.id == data.mapping_id).first()
        if not mapping:
            return None

        review = ReviewRecord(
            mapping_id=data.mapping_id,
            reviewer=data.reviewer,
            human_decision=data.human_decision,
            target_fhir_element_override=data.target_fhir_element_override,
            comment=data.comment,
        )
        db.add(review)
        db.flush()

        audit = AuditEvent(
            project_id=mapping.project_id,
            event_type="HUMAN_REVIEW_RECORDED",
            description=f"Field '{mapping.legacy_field}' reviewed by '{data.reviewer}': Decision '{data.human_decision}'",
            user=data.reviewer,
        )
        db.add(audit)
        db.commit()
        db.refresh(review)

        return ReviewResponse(
            id=review.id,
            mapping_id=review.mapping_id,
            reviewer=review.reviewer,
            human_decision=review.human_decision,
            target_fhir_element_override=review.target_fhir_element_override,
            comment=review.comment,
            reviewed_at=review.reviewed_at,
        )

    @staticmethod
    def get_review_queue(
        db: Session,
        project_id: Optional[str] = None,
        only_unreviewed: bool = True
    ) -> List[MappingRecordResponse]:
        """Fetch all fields flagged by the automated decision engine as REVIEW."""
        query = db.query(MappingRecord).filter(MappingRecord.automated_decision == "REVIEW")
        if project_id:
            query = query.filter(MappingRecord.project_id == project_id)

        records = query.order_by(MappingRecord.created_at.desc()).all()
        results = []
        for r in records:
            if only_unreviewed and len(r.reviews) > 0:
                continue
            results.append(MappingService._to_response(r))
        return results
