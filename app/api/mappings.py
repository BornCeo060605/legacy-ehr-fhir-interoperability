from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.api_schemas import MappingRecordResponse
from app.services.mapping_service import MappingService

router = APIRouter(prefix="/api/mappings", tags=["Mappings"])


@router.get("", response_model=List[MappingRecordResponse])
def list_mappings(
    project_id: Optional[str] = None,
    run_id: Optional[str] = None,
    database_name: Optional[str] = None,
    decision: Optional[str] = None,
    resource: Optional[str] = None,
    search: Optional[str] = None,
    min_confidence: Optional[float] = None,
    max_confidence: Optional[float] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    records, total = MappingService.get_mappings(
        db=db,
        project_id=project_id,
        run_id=run_id,
        database_name=database_name,
        decision=decision,
        resource=resource,
        search=search,
        min_confidence=min_confidence,
        max_confidence=max_confidence,
        skip=skip,
        limit=limit,
    )
    return records


@router.get("/{mapping_id}", response_model=MappingRecordResponse)
def get_mapping_detail(mapping_id: str, db: Session = Depends(get_db)):
    rec = MappingService.get_mapping(db, mapping_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Mapping record not found")
    return rec
