import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entities import AnalysisRun, DatabaseEntity, AuditEvent
from app.schemas.api_schemas import AnalysisRunCreate, AnalysisRunResponse
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])


@router.post("/start", response_model=AnalysisRunResponse)
def start_analysis(
    data: AnalysisRunCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Resolve database
    db_entity = None
    if data.database_id:
        db_entity = db.query(DatabaseEntity).filter(DatabaseEntity.id == data.database_id).first()
    elif data.database_path:
        db_entity = db.query(DatabaseEntity).filter(DatabaseEntity.file_path == data.database_path).first()

    if not db_entity:
        raise HTTPException(status_code=400, detail="Valid database_id or database_path required.")

    business_run_id = f"RUN_{uuid.uuid4().hex[:8].upper()}"

    # Create run record
    run_obj = AnalysisRun(
        project_id=data.project_id,
        database_id=db_entity.id,
        run_id=business_run_id,
        database_name=db_entity.name,
        status="PENDING",
        current_stage="Queued",
        llm_provider=data.provider or "openrouter",
        llm_model=data.model or "meta-llama/llama-3.3-70b-instruct",
    )
    db.add(run_obj)
    db.flush()

    audit = AuditEvent(
        project_id=data.project_id,
        event_type="ANALYSIS_QUEUED",
        description=f"Phase 1 Run '{business_run_id}' queued for database '{db_entity.name}'",
    )
    db.add(audit)
    db.commit()
    db.refresh(run_obj)

    # Launch actual pipeline in background task
    background_tasks.add_task(
        AnalysisService.execute_phase1_pipeline,
        run_record_id=run_obj.id,
        db_path=db_entity.file_path,
        provider_name=data.provider,
        model_name=data.model,
        limit=data.limit,
    )

    return run_obj


@router.get("/runs", response_model=List[AnalysisRunResponse])
def list_runs(project_id: Optional[str] = None, db: Session = Depends(get_db)):
    return AnalysisService.get_runs(db, project_id=project_id)


@router.get("/runs/{run_id}", response_model=AnalysisRunResponse)
def get_run(run_id: str, db: Session = Depends(get_db)):
    run_obj = AnalysisService.get_run(db, run_id)
    if not run_obj:
        run_obj = AnalysisService.get_run_by_business_id(db, run_id)
    if not run_obj:
        raise HTTPException(status_code=404, detail="Analysis run not found")
    return run_obj


@router.get("/runs/{run_id}/stream")
async def stream_run_events(run_id: str, db: Session = Depends(get_db)):
    """SSE endpoint streaming live pipeline execution events."""
    run_obj = AnalysisService.get_run(db, run_id)
    if not run_obj:
        run_obj = AnalysisService.get_run_by_business_id(db, run_id)
    if not run_obj:
        raise HTTPException(status_code=404, detail="Analysis run not found")

    return StreamingResponse(
        AnalysisService.subscribe_run_stream(run_obj.run_id),
        media_type="text/event-stream"
    )
