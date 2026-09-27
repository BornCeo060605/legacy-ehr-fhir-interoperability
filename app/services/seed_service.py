"""
Initial Application Data Seeder.
Synchronizes existing Phase 1 completed hospital reports and profiles into SQLite app.db
so the application starts fully loaded with real clinical analysis data.
"""

import os
import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.entities import Project, DatabaseEntity, AnalysisRun, MappingRecord, AuditEvent
from app.services.database_service import DatabaseService

logger = logging.getLogger(__name__)


def seed_existing_phase1_data(db: Session):
    """Seed existing Phase 1 runs if not already seeded."""
    # 1. Check or create Default Project
    project = db.query(Project).filter(Project.name == "Enterprise Healthcare Interoperability").first()
    if not project:
        project = Project(
            name="Enterprise Healthcare Interoperability",
            description="Autonomous, evidence-grounded semantic discovery and HL7 FHIR R4 mapping across multi-dialect hospital EHR databases.",
            fhir_version="4.0.1",
            status="ACTIVE",
        )
        db.add(project)
        db.flush()

        audit = AuditEvent(
            project_id=project.id,
            event_type="SYSTEM_INITIALIZATION",
            description="Initialized Enterprise Healthcare Interoperability Project",
            user="system",
        )
        db.add(audit)
        db.commit()

    # 2. Register Existing Databases
    hospitals = [
        ("hospital_a.db", "Hospital A (Clean / Normalized Dialect)"),
        ("hospital_b.db", "Hospital B (Abbreviated / Coded Dialect)"),
        ("hospital_c.db", "Hospital C (Cryptic / Held-Out Test Dialect)"),
    ]

    for db_filename, friendly_name in hospitals:
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", db_filename))
        if not os.path.exists(db_path):
            continue

        db_entity = DatabaseService.register_database(
            db=db,
            project_id=project.id,
            name=db_filename,
            file_path=db_path,
            is_demo=True,
        )

        # 3. Check for completed report JSON
        report_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "outputs", "reports", f"{db_filename}_phase1_report.json")
        )
        if not os.path.exists(report_path):
            continue

        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report_data = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load {report_path}: {e}")
            continue

        business_run_id = report_data.get("run_id", f"RUN_{db_filename}")
        existing_run = db.query(AnalysisRun).filter(AnalysisRun.run_id == business_run_id).first()
        if existing_run:
            continue

        # Create AnalysisRun
        total_fields = report_data.get("total_fields", 30)
        accepted = report_data.get("accepted_count", 0)
        review = report_data.get("review_count", 0)
        unsupported = report_data.get("unsupported_count", 0)

        run_obj = AnalysisRun(
            project_id=project.id,
            database_id=db_entity.id,
            run_id=business_run_id,
            database_name=db_filename,
            status="COMPLETED",
            current_stage="Completed",
            progress_percentage=100.0,
            llm_provider=report_data.get("llm_provider", "openrouter"),
            llm_model=report_data.get("llm_model", "meta-llama/llama-3.3-70b-instruct"),
            total_fields=total_fields,
            accepted_count=accepted,
            review_count=review,
            unsupported_count=unsupported,
            elapsed_seconds=1500.0,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )
        db.add(run_obj)
        db.flush()

        # Seed Mapping Records
        field_reports = report_data.get("field_reports", [])
        for fr in field_reports:
            fc = fr.get("fhir_candidate") or {}
            conf = fr.get("confidence_breakdown") or {}
            dec = fr.get("decision") or {}

            mapping_rec = MappingRecord(
                run_id=run_obj.id,
                project_id=project.id,
                database_name=db_filename,
                table_name=fr.get("table_name", ""),
                column_name=fr.get("column_name", ""),
                legacy_field=fr.get("legacy_field", ""),
                semantic_meaning=fr.get("semantic_meaning", ""),
                observed_facts_json=json.dumps(fr.get("observed_facts", [])),
                inferred_facts_json=json.dumps(fr.get("inferred_facts", [])),
                fhir_resource=fc.get("target_resource", "Unknown"),
                fhir_element=fc.get("target_path", "(none)"),
                datatype=fc.get("target_element_type", "string"),
                cardinality=fc.get("cardinality", "0..1"),
                binding_valueset=fc.get("binding_valueset"),
                rationale=fc.get("rationale"),
                retrieved_evidence_summary_json=json.dumps(fr.get("retrieved_evidence_summary", [])),
                mapping_confidence=round(conf.get("mapping_confidence", 0.0), 2),
                evidence_strength=conf.get("evidence_strength", "MODERATE"),
                automated_decision=dec.get("decision", "REVIEW"),
                rule_id=dec.get("rule_id", "R3_MANUAL_REVIEW_REQUIRED"),
                decision_reason=dec.get("reason"),
                provenance_json=json.dumps(fr.get("provenance", [])),
            )
            db.add(mapping_rec)

        db.commit()
        logger.info(f"Seeded {len(field_reports)} mappings for {db_filename} (Run: {business_run_id})")
