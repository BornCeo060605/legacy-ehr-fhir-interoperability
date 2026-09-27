import json
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entities import AuditEvent
from app.schemas.api_schemas import AuditEventResponse

router = APIRouter(prefix="/api/audit", tags=["Audit Trail"])


@router.get("", response_model=List[AuditEventResponse])
def list_audit_events(
    project_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(AuditEvent)
    if project_id:
        query = query.filter(AuditEvent.project_id == project_id)

    events = query.order_by(AuditEvent.created_at.desc()).limit(limit).all()
    results = []
    for e in events:
        details = json.loads(e.details_json) if e.details_json else None
        results.append(
            AuditEventResponse(
                id=e.id,
                project_id=e.project_id,
                event_type=e.event_type,
                description=e.description,
                details=details,
                user=e.user,
                created_at=e.created_at,
            )
        )
    return results
