"""
Analysis Orchestration & Real-Time Pipeline Service.
Executes the genuine 8-stage Phase 1 research pipeline in background workers,
persists auditable mapping records, and broadcasts Server-Sent Events (SSE).
"""

import os
import sys
import json
import time
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, AsyncGenerator, List
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.entities import AnalysisRun, MappingRecord, AuditEvent, DatabaseEntity
from models.schemas import MappingReportItem
from tools.schema_profiler import SchemaProfiler
from agents.schema_intelligence import SchemaIntelligenceAgent
from retrieval.strategy import RetrievalStrategyPlanner
from retrieval.hybrid_retriever import HybridRetriever
from agents.semantic_agent import SemanticAgent
from agents.fhir_mapping_agent import FHIRMappingAgent
from models.confidence_decision_engine import ConfidenceEngine, DecisionEngine
from resources.resource_manager import ResourceManager
from models.llm_provider import LLMProvider


# Global in-memory broadcast queues for live SSE streams
RUN_EVENT_QUEUES: Dict[str, List[asyncio.Queue]] = {}


def broadcast_event(run_id: str, event_type: str, data: Dict[str, Any]):
    """Push an event to all subscribers listening to this run_id."""
    queues = RUN_EVENT_QUEUES.get(run_id, [])
    payload = json.dumps({"type": event_type, "timestamp": datetime.utcnow().isoformat(), "data": data})
    for q in queues:
        try:
            q.put_nowait(payload)
        except Exception:
            pass


class AnalysisService:

    @staticmethod
    def get_runs(db: Session, project_id: Optional[str] = None) -> List[AnalysisRun]:
        query = db.query(AnalysisRun)
        if project_id:
            query = query.filter(AnalysisRun.project_id == project_id)
        return query.order_by(AnalysisRun.started_at.desc()).all()

    @staticmethod
    def get_run(db: Session, run_id: str) -> Optional[AnalysisRun]:
        return db.query(AnalysisRun).filter(AnalysisRun.id == run_id).first()

    @staticmethod
    def get_run_by_business_id(db: Session, business_run_id: str) -> Optional[AnalysisRun]:
        return db.query(AnalysisRun).filter(AnalysisRun.run_id == business_run_id).first()

    @staticmethod
    async def subscribe_run_stream(run_id: str) -> AsyncGenerator[str, None]:
        """Async generator yielding SSE formatted messages for a run."""
        queue: asyncio.Queue = asyncio.Queue()
        if run_id not in RUN_EVENT_QUEUES:
            RUN_EVENT_QUEUES[run_id] = []
        RUN_EVENT_QUEUES[run_id].append(queue)

        try:
            # Send initial connected event
            yield f"event: connected\ndata: {json.dumps({'run_id': run_id, 'status': 'connected'})}\n\n"
            while True:
                msg = await queue.get()
                yield f"event: pipeline_event\ndata: {msg}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            if run_id in RUN_EVENT_QUEUES and queue in RUN_EVENT_QUEUES[run_id]:
                RUN_EVENT_QUEUES[run_id].remove(queue)

    @staticmethod
    def execute_phase1_pipeline(
        run_record_id: str,
        db_path: str,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
        limit: Optional[int] = None,
    ):
        """
        Synchronous worker thread running the actual 8-stage Phase 1 pipeline.
        Creates its own database session.
        """
        db = SessionLocal()
        run_obj = db.query(AnalysisRun).filter(AnalysisRun.id == run_record_id).first()
        if not run_obj:
            db.close()
            return

        run_id = run_obj.run_id
        start_time = time.time()
        run_obj.status = "RUNNING"
        run_obj.current_stage = "Stage 1: Deterministic Schema Profiling"
        run_obj.progress_percentage = 5.0
        db.commit()

        broadcast_event(run_id, "run_started", {
            "run_id": run_id,
            "database": run_obj.database_name,
            "provider": provider_name or "openrouter",
            "model": model_name or "meta-llama/llama-3.3-70b-instruct",
        })

        try:
            # Initialize pipeline components
            llm_provider = LLMProvider(provider=provider_name, model=model_name)
            resource_mgr = ResourceManager()
            schema_agent = SchemaIntelligenceAgent(llm_provider=llm_provider)
            planner = RetrievalStrategyPlanner()
            hybrid_retriever = HybridRetriever()
            semantic_agent = SemanticAgent(llm_provider=llm_provider)
            fhir_agent = FHIRMappingAgent(llm_provider=llm_provider)
            conf_engine = ConfidenceEngine()
            decision_engine = DecisionEngine()

            # 1. Deterministic Schema Profiling
            broadcast_event(run_id, "stage_started", {"stage_index": 1, "stage_name": "Deterministic Schema Profiling"})
            profiler = SchemaProfiler(db_path)
            db_profile = profiler.profile_database()
            
            # Count fields
            total_columns = sum(len(t.columns) for t in db_profile.tables.values())
            max_fields = min(limit, total_columns) if limit else total_columns
            run_obj.total_fields = max_fields
            run_obj.current_stage = "Stage 2: Inspecting Knowledge Resources"
            run_obj.progress_percentage = 10.0
            db.commit()

            broadcast_event(run_id, "stage_started", {"stage_index": 2, "stage_name": "Knowledge Resource Manifestation"})
            manifests = resource_mgr.get_all_manifests()

            # Loop through fields
            processed_count = 0
            accepted_cnt = 0
            review_cnt = 0
            unsupported_cnt = 0

            for tbl_name, tbl_prof in db_profile.tables.items():
                for col_name, col_fact in tbl_prof.columns.items():
                    if limit and processed_count >= limit:
                        break

                    field_tag = f"{tbl_name}.{col_name}"
                    run_obj.current_stage = f"Analyzing {field_tag} ({processed_count + 1}/{max_fields})"
                    progress = 10.0 + (float(processed_count) / float(max_fields)) * 85.0
                    run_obj.progress_percentage = round(progress, 1)
                    db.commit()

                    broadcast_event(run_id, "field_started", {
                        "field_index": processed_count + 1,
                        "total_fields": max_fields,
                        "field": field_tag,
                        "table": tbl_name,
                        "column": col_name,
                    })

                    # Stage 3: Schema Intelligence
                    intel_res = schema_agent.analyze_column(
                        col_fact, tbl_prof, db_profile.observed_value_overlaps
                    )

                    # Stage 4: Retrieval Strategy
                    retrieval_plan = planner.plan_retrieval(col_fact, intel_res.role)

                    # Stage 5: Hybrid Evidence Retrieval
                    retrieved_evidence = hybrid_retriever.execute_plan(retrieval_plan)

                    # Stage 6: Clinical Semantic Agent
                    semantic_interp = semantic_agent.interpret(
                        col_fact,
                        intel_res.role,
                        retrieval_plan,
                        retrieved_evidence,
                        db_profile.observed_value_overlaps,
                    )

                    # Stage 7: FHIR Mapping Agent
                    fhir_candidate = fhir_agent.propose_mapping(
                        col_fact, semantic_interp, retrieved_evidence
                    )

                    # Stage 8: Confidence & Decision Engine
                    confidence_breakdown = conf_engine.calculate(
                        col_fact, semantic_interp, retrieved_evidence, fhir_candidate
                    )
                    decision = decision_engine.decide(
                        confidence_breakdown, fhir_candidate, col_fact
                    )

                    # Track counts
                    if decision.decision == "ACCEPTED":
                        accepted_cnt += 1
                    elif decision.decision == "REVIEW":
                        review_cnt += 1
                    elif decision.decision == "UNSUPPORTED":
                        unsupported_cnt += 1

                    ev_summary = [e.description for e in retrieved_evidence[:4]] or ["No external evidence retrieved"]

                    # Persist Mapping Record
                    mapping_rec = MappingRecord(
                        run_id=run_obj.id,
                        project_id=run_obj.project_id,
                        database_name=run_obj.database_name,
                        table_name=tbl_name,
                        column_name=col_name,
                        legacy_field=field_tag,
                        semantic_meaning=semantic_interp.semantic_meaning,
                        observed_facts_json=json.dumps(semantic_interp.observed_facts),
                        inferred_facts_json=json.dumps(semantic_interp.inferred_facts),
                        fhir_resource=fhir_candidate.target_resource if fhir_candidate else "Unknown",
                        fhir_element=fhir_candidate.target_path if fhir_candidate else "(none)",
                        datatype=fhir_candidate.target_element_type if fhir_candidate else "string",
                        cardinality=fhir_candidate.cardinality if fhir_candidate else "0..1",
                        binding_valueset=fhir_candidate.binding_valueset if fhir_candidate else None,
                        rationale=fhir_candidate.rationale if fhir_candidate else None,
                        retrieved_evidence_summary_json=json.dumps(ev_summary),
                        mapping_confidence=round(confidence_breakdown.mapping_confidence, 2),
                        evidence_strength=confidence_breakdown.evidence_strength,
                        automated_decision=decision.decision,
                        rule_id=decision.rule_id,
                        decision_reason=decision.reason,
                        provenance_json=json.dumps([
                            f"Database Checksum: {db_profile.checksum_sha256[:12]}...",
                            "Deterministic Schema Profiler",
                            f"Schema Intelligence ({llm_provider.provider})",
                            f"Hybrid Retrieval ({', '.join(retrieval_plan.included_sources)})",
                            f"Semantic Agent ({llm_provider.model})",
                            f"FHIR Mapping Agent ({fhir_candidate.target_path if fhir_candidate else 'None'})",
                            f"Deterministic Decision Engine ({decision.rule_id})",
                        ]),
                    )
                    db.add(mapping_rec)
                    db.commit()

                    broadcast_event(run_id, "field_completed", {
                        "field": field_tag,
                        "fhir_element": mapping_rec.fhir_element,
                        "confidence": mapping_rec.mapping_confidence,
                        "evidence_strength": mapping_rec.evidence_strength,
                        "decision": mapping_rec.automated_decision,
                        "rule_id": mapping_rec.rule_id,
                    })

                    processed_count += 1
                if limit and processed_count >= limit:
                    break

            # Finish run
            elapsed = time.time() - start_time
            run_obj.status = "COMPLETED"
            run_obj.current_stage = "Completed"
            run_obj.progress_percentage = 100.0
            run_obj.accepted_count = accepted_cnt
            run_obj.review_count = review_cnt
            run_obj.unsupported_count = unsupported_cnt
            run_obj.elapsed_seconds = round(elapsed, 2)
            run_obj.completed_at = datetime.utcnow()

            audit = AuditEvent(
                project_id=run_obj.project_id,
                event_type="ANALYSIS_COMPLETED",
                description=f"Phase 1 Run '{run_id}' completed for '{run_obj.database_name}' in {elapsed:.1f}s. Accepted: {accepted_cnt}, Review: {review_cnt}, Unsupported: {unsupported_cnt}",
            )
            db.add(audit)
            db.commit()

            broadcast_event(run_id, "run_completed", {
                "run_id": run_id,
                "elapsed_seconds": round(elapsed, 2),
                "total_fields": max_fields,
                "accepted_count": accepted_cnt,
                "review_count": review_cnt,
                "unsupported_count": unsupported_cnt,
            })

        except Exception as e:
            elapsed = time.time() - start_time
            run_obj.status = "FAILED"
            run_obj.error_message = str(e)
            run_obj.elapsed_seconds = round(elapsed, 2)
            run_obj.completed_at = datetime.utcnow()
            db.commit()

            broadcast_event(run_id, "run_failed", {
                "run_id": run_id,
                "error": str(e),
            })
        finally:
            db.close()
