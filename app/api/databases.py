import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.api_schemas import DatabaseResponse
from app.services.database_service import DatabaseService

router = APIRouter(prefix="/api/databases", tags=["Databases"])


def _to_response(db_entity) -> DatabaseResponse:
    profile_summary = None
    full_prof = None
    if db_entity.profile_json:
        try:
            full_prof = json.loads(db_entity.profile_json)
            profile_summary = full_prof.get("summary")
        except Exception:
            pass

    return DatabaseResponse(
        id=db_entity.id,
        project_id=db_entity.project_id,
        name=db_entity.name,
        file_path=db_entity.file_path,
        sha256_checksum=db_entity.sha256_checksum,
        sha256=db_entity.sha256_checksum,
        file_size_bytes=db_entity.file_size_bytes,
        table_count=db_entity.table_count,
        total_row_count=db_entity.total_row_count,
        row_count=db_entity.total_row_count,
        status="VERIFIED",
        is_demo=db_entity.is_demo,
        created_at=db_entity.created_at,
        profile_summary=profile_summary,
        profile=full_prof,
    )


@router.post("/upload", response_model=DatabaseResponse)
async def upload_database(
    project_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        content = await file.read()
        entity = DatabaseService.import_uploaded_database(
            db=db,
            project_id=project_id,
            filename=file.filename,
            content=content
        )
        return _to_response(entity)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[DatabaseResponse])
def list_databases(project_id: Optional[str] = None, db: Session = Depends(get_db)):
    entities = DatabaseService.get_databases(db, project_id=project_id)
    return [_to_response(e) for e in entities]


@router.get("/{database_id}", response_model=DatabaseResponse)
def get_database(database_id: str, db: Session = Depends(get_db)):
    entity = DatabaseService.get_database(db, database_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Database not found")
    return _to_response(entity)


@router.get("/{database_id}/schema")
def get_schema(database_id: str, db: Session = Depends(get_db)):
    profile = DatabaseService.get_schema_profile(db, database_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Schema profile not found for database")
    return profile
