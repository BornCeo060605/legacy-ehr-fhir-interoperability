import time
from datetime import datetime
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.entities import Project, DatabaseEntity, AnalysisRun, MappingRecord, AuditEvent
from app.schemas.api_schemas import SystemHealthResponse, DashboardStatsResponse, AnalysisRunResponse
from app.services.resource_service import ResourceService
from models.llm_provider import LLMProvider

router = APIRouter(tags=["Health & Dashboard"])

APP_START_TIME = time.time()


@router.get("/api/health", response_model=SystemHealthResponse)
def get_system_health(db: Session = Depends(get_db)):
    uptime = time.time() - APP_START_TIME

    # Check DB
    db_status = "HEALTHY"
    try:
        db.execute(func.now())
    except Exception:
        db_status = "UNHEALTHY"

    # Check Resources
    res_items = ResourceService.get_resource_statuses()
    avail_count = sum(1 for r in res_items if r.status == "AVAILABLE")
    res_status = "HEALTHY" if avail_count >= 3 else "DEGRADED"

    # LLM status
    provider = LLMProvider()
    llm_status = "HEALTHY" if (provider._openrouter_key or provider._groq_keys) else "DEGRADED"

    overall = "HEALTHY" if (db_status == "HEALTHY" and res_status != "UNAVAILABLE") else "DEGRADED"
    audit_count = db.query(AuditEvent).count()

    return SystemHealthResponse(
        status=overall,
        version="1.0.0",
        fhir_version="4.0.1",
        uptime_seconds=round(uptime, 1),
        database_status=db_status,
        knowledge_resources_status=res_status,
        llm_provider_status=llm_status,
        llm_active_provider=provider.provider,
        llm_active_model=provider.model,
        total_audit_events=audit_count,
        timestamp=datetime.utcnow(),
        components={
            "database": db_status,
            "knowledge_resources": res_status,
            "llm_provider": llm_status,
            "active_model": provider.model,
            "vector_store": "ONLINE",
        },
    )


@router.get("/api/dashboard/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(project_id: str = None, db: Session = Depends(get_db)):
    p_query = db.query(Project)
    db_query = db.query(DatabaseEntity)
    r_query = db.query(AnalysisRun)
    m_query = db.query(MappingRecord)

    if project_id:
        db_query = db_query.filter(DatabaseEntity.project_id == project_id)
        r_query = r_query.filter(AnalysisRun.project_id == project_id)
        m_query = m_query.filter(MappingRecord.project_id == project_id)

    total_projects = p_query.count()
    total_databases = db_query.count()
    total_runs = r_query.count()
    total_fields = m_query.count()

    accepted_cnt = m_query.filter(MappingRecord.automated_decision == "ACCEPTED").count()
    review_cnt = m_query.filter(MappingRecord.automated_decision == "REVIEW").count()
    unsupported_cnt = m_query.filter(MappingRecord.automated_decision == "UNSUPPORTED").count()

    acc_rate = (accepted_cnt / total_fields * 100.0) if total_fields > 0 else 0.0
    rev_rate = (review_cnt / total_fields * 100.0) if total_fields > 0 else 0.0
    uns_rate = (unsupported_cnt / total_fields * 100.0) if total_fields > 0 else 0.0

    avg_conf = db.query(func.avg(MappingRecord.mapping_confidence))
    if project_id:
        avg_conf = avg_conf.filter(MappingRecord.project_id == project_id)
    avg_conf_val = avg_conf.scalar() or 0.0

    # Resource distribution
    res_dist = {}
    res_rows = (
        db.query(MappingRecord.fhir_resource, func.count(MappingRecord.id))
        .filter(MappingRecord.fhir_resource != "Unknown")
        .group_by(MappingRecord.fhir_resource)
        .all()
    )
    for res_name, count in res_rows:
        res_dist[res_name] = count

    # Decision distribution
    dec_dist = {
        "ACCEPTED": accepted_cnt,
        "REVIEW": review_cnt,
        "UNSUPPORTED": unsupported_cnt,
    }

    # Hospital breakdown
    hosp_breakdown = {}
    hosp_dbs = db.query(MappingRecord.database_name).distinct().all()
    for (h_name,) in hosp_dbs:
        h_mappings = db.query(MappingRecord).filter(MappingRecord.database_name == h_name)
        h_total = h_mappings.count()
        h_acc = h_mappings.filter(MappingRecord.automated_decision == "ACCEPTED").count()
        h_rev = h_mappings.filter(MappingRecord.automated_decision == "REVIEW").count()
        h_uns = h_mappings.filter(MappingRecord.automated_decision == "UNSUPPORTED").count()
        h_avg_conf = db.query(func.avg(MappingRecord.mapping_confidence)).filter(MappingRecord.database_name == h_name).scalar() or 0.0
        hosp_breakdown[h_name] = {
            "total": h_total,
            "accepted": h_acc,
            "review": h_rev,
            "unsupported": h_uns,
            "avg_confidence": round(h_avg_conf, 2),
        }

    recent_runs = r_query.order_by(AnalysisRun.started_at.desc()).limit(5).all()

    return DashboardStatsResponse(
        total_projects=total_projects,
        total_databases=total_databases,
        total_runs=total_runs,
        total_fields_analyzed=total_fields,
        accepted_count=accepted_cnt,
        review_count=review_cnt,
        unsupported_count=unsupported_cnt,
        acceptance_rate=round(acc_rate, 1),
        review_rate=round(rev_rate, 1),
        unsupported_rate=round(uns_rate, 1),
        avg_confidence=round(avg_conf_val, 2),
        average_confidence=round(avg_conf_val, 2),
        hospital_breakdown=hosp_breakdown,
        fhir_resource_distribution=res_dist,
        decision_distribution=dec_dist,
        recent_runs=[AnalysisRunResponse.model_validate(r) for r in recent_runs],
    )
