"""
Database Management & Profiling Service.
Handles legacy EHR SQLite uploads, cryptographic checksums, integrity verification,
and detailed relational schema inspection.
"""

import os
import json
import hashlib
import sqlite3
import shutil
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.entities import DatabaseEntity, AuditEvent
from tools.schema_profiler import SchemaProfiler


UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)


class DatabaseService:

    @staticmethod
    def calculate_sha256(file_path: str) -> str:
        sha = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                sha.update(chunk)
        return sha.hexdigest()

    @staticmethod
    def register_database(
        db: Session,
        project_id: str,
        name: str,
        file_path: str,
        is_demo: bool = False
    ) -> DatabaseEntity:
        """Register an existing database file on disk."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Database file not found: {file_path}")

        checksum = DatabaseService.calculate_sha256(file_path)
        file_size = os.path.getsize(file_path)

        # Profile schema deterministically
        profiler = SchemaProfiler(file_path)
        profile = profiler.profile_database()
        profile_json = json.dumps(profile.model_dump(), default=str)

        total_rows = profile.summary.get("total_rows", 0)
        table_count = profile.summary.get("total_tables", 0)

        # Check if already registered
        existing = db.query(DatabaseEntity).filter(
            DatabaseEntity.project_id == project_id,
            DatabaseEntity.sha256_checksum == checksum
        ).first()

        if existing:
            return existing

        db_entity = DatabaseEntity(
            project_id=project_id,
            name=name,
            file_path=file_path,
            sha256_checksum=checksum,
            file_size_bytes=file_size,
            table_count=table_count,
            total_row_count=total_rows,
            profile_json=profile_json,
            is_demo=is_demo,
        )
        db.add(db_entity)
        db.flush()

        audit = AuditEvent(
            project_id=project_id,
            event_type="DATABASE_REGISTERED",
            description=f"Database '{name}' registered ({table_count} tables, {total_rows:,} rows, SHA256: {checksum[:8]}...)",
        )
        db.add(audit)
        db.commit()
        db.refresh(db_entity)
        return db_entity

    @staticmethod
    def import_uploaded_database(
        db: Session,
        project_id: str,
        filename: str,
        content: bytes
    ) -> DatabaseEntity:
        """Process and safely persist an uploaded SQLite database."""
        # Sanitize filename
        safe_name = os.path.basename(filename)
        valid_exts = [".db", ".sqlite", ".sqlite3", ".db3"]
        if not any(safe_name.lower().endswith(ext) for ext in valid_exts):
            raise ValueError(f"Invalid file extension. Expected one of {valid_exts}")

        dest_path = os.path.join(UPLOAD_DIR, safe_name)
        # Avoid collisions
        counter = 1
        base, ext = os.path.splitext(safe_name)
        while os.path.exists(dest_path):
            dest_path = os.path.join(UPLOAD_DIR, f"{base}_{counter}{ext}")
            counter += 1

        with open(dest_path, "wb") as f:
            f.write(content)

        return DatabaseService.register_database(
            db=db,
            project_id=project_id,
            name=safe_name,
            file_path=dest_path,
            is_demo=False
        )

    @staticmethod
    def get_databases(db: Session, project_id: Optional[str] = None) -> List[DatabaseEntity]:
        query = db.query(DatabaseEntity)
        if project_id:
            query = query.filter(DatabaseEntity.project_id == project_id)
        return query.order_by(DatabaseEntity.created_at.desc()).all()

    @staticmethod
    def get_database(db: Session, database_id: str) -> Optional[DatabaseEntity]:
        return db.query(DatabaseEntity).filter(DatabaseEntity.id == database_id).first()

    @staticmethod
    def get_schema_profile(db: Session, database_id: str) -> Optional[Dict[str, Any]]:
        entity = db.query(DatabaseEntity).filter(DatabaseEntity.id == database_id).first()
        if not entity or not entity.profile_json:
            return None
        return json.loads(entity.profile_json)
