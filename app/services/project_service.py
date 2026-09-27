"""
Project Management Service.
Handles project lifecycle, metadata, and relations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.entities import Project, DatabaseEntity, AnalysisRun, MappingRecord, AuditEvent
from app.schemas.api_schemas import ProjectCreate, ProjectResponse


class ProjectService:

    @staticmethod
    def create_project(db: Session, data: ProjectCreate) -> Project:
        project = Project(
            name=data.name,
            description=data.description,
            fhir_version=data.fhir_version,
            status="ACTIVE",
        )
        db.add(project)
        db.flush()

        audit = AuditEvent(
            project_id=project.id,
            event_type="PROJECT_CREATED",
            description=f"Project '{project.name}' initialized for FHIR {project.fhir_version}",
        )
        db.add(audit)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def get_projects(db: Session) -> List[ProjectResponse]:
        projects = db.query(Project).order_by(Project.created_at.desc()).all()
        result = []
        for p in projects:
            db_count = db.query(DatabaseEntity).filter(DatabaseEntity.project_id == p.id).count()
            run_count = db.query(AnalysisRun).filter(AnalysisRun.project_id == p.id).count()
            map_count = db.query(MappingRecord).filter(MappingRecord.project_id == p.id).count()

            resp = ProjectResponse(
                id=p.id,
                name=p.name,
                description=p.description,
                fhir_version=p.fhir_version,
                status=p.status,
                created_at=p.created_at,
                updated_at=p.updated_at,
                database_count=db_count,
                run_count=run_count,
                mapping_count=map_count,
            )
            result.append(resp)
        return result

    @staticmethod
    def get_project(db: Session, project_id: str) -> Optional[Project]:
        return db.query(Project).filter(Project.id == project_id).first()

    @staticmethod
    def delete_project(db: Session, project_id: str) -> bool:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return False
        db.delete(project)
        db.commit()
        return True
