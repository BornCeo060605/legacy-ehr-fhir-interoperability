from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.api_schemas import ReviewCreate, ReviewResponse, MappingRecordResponse
from app.services.review_service import ReviewService

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


@router.post("", response_model=ReviewResponse)
def submit_review(data: ReviewCreate, db: Session = Depends(get_db)):
    result = ReviewService.record_review(db, data)
    if not result:
        raise HTTPException(status_code=404, detail="Mapping record not found")
    return result


@router.get("/queue", response_model=List[MappingRecordResponse])
def get_review_queue(
    project_id: Optional[str] = None,
    only_unreviewed: bool = True,
    db: Session = Depends(get_db)
):
    return ReviewService.get_review_queue(db, project_id=project_id, only_unreviewed=only_unreviewed)
