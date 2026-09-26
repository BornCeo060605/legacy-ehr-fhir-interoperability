"""
Phase 1 End-to-End Orchestrator and Mapping Report Generator.
Executes the complete evidence-based pipeline:
  Legacy EHR -> Profiler -> Schema Intelligence -> Retrieval Strategy
  -> Hybrid Evidence Retrieval -> Semantic Agent -> FHIR Mapping Agent
  -> Confidence Engine -> Decision Engine -> Auditable Mapping Report.
Usage:
    python scripts/run_phase1.py [--db data/hospital_a.db] [--provider openrouter] [--limit 30]
"""

import os
import sys
import json
import time
import uuid
import platform
import argparse
from typing import Optional, List, Dict, Any
from datetime import datetime
from tabulate import tabulate

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.schemas import (
    DatabaseProfile,
    MappingReportItem,
    Phase1AuditReport,
)
from tools.schema_profiler import SchemaProfiler
from agents.schema_intelligence import SchemaIntelligenceAgent
from retrieval.strategy import RetrievalStrategyPlanner
from retrieval.hybrid_retriever import HybridRetriever
from agents.semantic_agent import SemanticAgent
from agents.fhir_mapping_agent import FHIRMappingAgent
from models.confidence_decision_engine import ConfidenceEngine, DecisionEngine
from resources.resource_manager import ResourceManager
from models.llm_provider import LLMProvider


class Phase1Pipeline:
    """
    End-to-End Phase 1 Orchestrator.
    """

    def __init__(self, provider_name: Optional[str] = None, model_name: Optional[str] = None):
        self.llm_provider = LLMProvider(provider=provider_name, model=model_name)
        self.resource_mgr = ResourceManager()
        self.schema_agent = SchemaIntelligenceAgent(llm_provider=self.llm_provider)
        self.planner = RetrievalStrategyPlanner()
        self.hybrid_retriever = HybridRetriever()
        self.semantic_agent = SemanticAgent(llm_provider=self.llm_provider)
        self.fhir_agent = FHIRMappingAgent(llm_provider=self.llm_provider)
        self.conf_engine = ConfidenceEngine()
        self.decision_engine = DecisionEngine()

    def run(self, db_path: str, limit: Optional[int] = None) -> Phase1AuditReport:
        run_id = f"PHASE1_RUN_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        start_time = time.time()

        print(f"\n{'='*80}")
        print(f"PHASE 1 PIPELINE: LEGACY EHR -> HL7 FHIR R4 MAPPING DISCOVERY")
        print(f"{'='*80}")
        print(f"Run ID:        {run_id}")
        print(f"Database:      {db_path}")
        print(f"LLM Provider:  {self.llm_provider.provider} (Model: {self.llm_provider.model})")
        print(f"Python:        {platform.python_version()}")

        # 1. Deterministic Schema Profiling
        print("\n[Step 1/8] Running Deterministic Schema Profiler...")
        profiler = SchemaProfiler(db_path)
        db_profile = profiler.profile_database()
        print(f"  -> Profiled {db_profile.summary['total_tables']} tables, {db_profile.summary['total_columns']} columns, {db_profile.summary['total_rows']:,} rows.")

        # 2. Collect Knowledge Source Manifests
        print("\n[Step 2/8] Inspecting Healthcare Knowledge Resources...")
        manifests = self.resource_mgr.get_all_manifests()
        manifest_dict = {k: v.model_dump() for k, v in manifests.items()}

        field_reports: list[MappingReportItem] = []
        table_summary_rows = []

        total_fields = sum(len(t.columns) for t in db_profile.tables.values())
        max_fields = min(limit, total_fields) if limit else total_fields
        print(f"\n[Steps 3-7/8] Processing {max_fields} legacy fields across evidence pipeline...\n")

        processed_count = 0
        for tbl_name, tbl_prof in db_profile.tables.items():
            for col_name, col_fact in tbl_prof.columns.items():
                if limit and processed_count >= limit:
                    break

                field_tag = f"{tbl_name}.{col_name}"
                print(f"[{processed_count + 1}/{max_fields}] Analyzing {field_tag}...", flush=True)

                # Step 3: Schema Intelligence Agent
                intel_res = self.schema_agent.analyze_column(
                    col_fact, tbl_prof, db_profile.observed_value_overlaps
                )

                # Step 4: Deterministic Retrieval Strategy
                retrieval_plan = self.planner.plan_retrieval(col_fact, intel_res.role)

                # Step 5: Hybrid Evidence Retrieval
                retrieved_evidence = self.hybrid_retriever.execute_plan(retrieval_plan)

                # Step 6: Semantic Agent
                semantic_interp = self.semantic_agent.interpret(
                    col_fact,
                    intel_res.role,
                    retrieval_plan,
                    retrieved_evidence,
                    db_profile.observed_value_overlaps,
                )

                # Step 7: FHIR Mapping Agent
                fhir_candidate = self.fhir_agent.propose_mapping(
                    col_fact, semantic_interp, retrieved_evidence
                )

                # Step 8: Deterministic Confidence & Final Decision Engine
                confidence_breakdown = self.conf_engine.calculate(
                    col_fact, semantic_interp, retrieved_evidence, fhir_candidate
                )
                decision = self.decision_engine.decide(
                    confidence_breakdown, fhir_candidate, col_fact
                )

                # Construct Evidence Summary
                ev_summary = [e.description for e in retrieved_evidence[:4]]
                if not ev_summary:
                    ev_summary = ["No external evidence retrieved (excluded or unpopulated)"]

                report_item = MappingReportItem(
                    legacy_field=field_tag,
                    table_name=tbl_name,
                    column_name=col_name,
                    semantic_meaning=semantic_interp.semantic_meaning,
                    observed_facts=semantic_interp.observed_facts,
                    inferred_facts=semantic_interp.inferred_facts,
                    retrieved_evidence_summary=ev_summary,
                    fhir_candidate=fhir_candidate,
                    confidence_breakdown=confidence_breakdown,
                    decision=decision,
                    provenance=[
                        f"Database Checksum: {db_profile.checksum_sha256[:12]}...",
                        "Deterministic Schema Profiler",
                        f"Schema Intelligence ({self.llm_provider.provider})",
                        f"Hybrid Retrieval ({', '.join(retrieval_plan.included_sources)})",
                        f"Semantic Agent ({self.llm_provider.model})",
                        f"FHIR Mapping Agent ({fhir_candidate.target_path if fhir_candidate else 'None'})",
                        f"Deterministic Decision Engine ({decision.rule_id})",
                    ],
                )
                field_reports.append(report_item)

                table_summary_rows.append([
                    field_tag,
                    fhir_candidate.target_path if fhir_candidate else "(none)",
                    f"{confidence_breakdown.mapping_confidence:.2f}",
                    confidence_breakdown.evidence_strength,
                    decision.decision,
                    decision.rule_id,
                ])

                processed_count += 1
            if limit and processed_count >= limit:
                break

        # Calculate statistics
        accepted_cnt = sum(1 for r in field_reports if r.decision.decision == "ACCEPTED")
        review_cnt = sum(1 for r in field_reports if r.decision.decision == "REVIEW")
        unsupported_cnt = sum(1 for r in field_reports if r.decision.decision == "UNSUPPORTED")

        audit_report = Phase1AuditReport(
            run_id=run_id,
            database_path=db_profile.database_path,
            database_name=db_profile.database_name,
            database_checksum_sha256=db_profile.checksum_sha256,
            llm_provider=self.llm_provider.provider,
            llm_model=self.llm_provider.model,
            total_fields=len(field_reports),
            accepted_count=accepted_cnt,
            review_count=review_cnt,
            unsupported_count=unsupported_cnt,
            field_reports=field_reports,
            knowledge_sources_manifest=manifest_dict,
        )

        # Print human-readable summary
        print(f"\n{'='*80}")
        print("PHASE 1 FHIR MAPPING DECISION SUMMARY")
        print(f"{'='*80}")
        print(tabulate(
            table_summary_rows,
            headers=["Legacy Field", "FHIR Candidate Path", "Confidence", "Evidence Strength", "Decision", "Rule ID"],
            tablefmt="github",
        ))

        print(f"\n{'='*80}")
        print("DECISION BREAKDOWN:")
        print(f"  - Total Fields Evaluated: {len(field_reports)}")
        print(f"  - ACCEPTED:               {accepted_cnt} ({accepted_cnt/len(field_reports):.1%})")
        print(f"  - REVIEW (Human triage):  {review_cnt} ({review_cnt/len(field_reports):.1%})")
        print(f"  - UNSUPPORTED:            {unsupported_cnt} ({unsupported_cnt/len(field_reports):.1%})")
        print(f"  - Total Time Elapsed:     {time.time() - start_time:.2f} seconds")
        print(f"{'='*80}\n")

        # Persist report formats
        self._persist_reports(audit_report)

        return audit_report

    def _persist_reports(self, audit_report: Phase1AuditReport):
        os.makedirs("outputs/reports", exist_ok=True)
        base_name = f"{audit_report.database_name}_phase1_report"

        # 1. JSON
        json_path = f"outputs/reports/{base_name}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(audit_report.model_dump_json(indent=2))
        print(f"Persisted JSON Report:  {json_path}")

        # 2. JSONL
        jsonl_path = f"outputs/reports/{base_name}.jsonl"
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for item in audit_report.field_reports:
                f.write(item.model_dump_json() + "\n")
        print(f"Persisted JSONL Log:    {jsonl_path}")

        # 3. Markdown Report (Full Audit Trail)
        md_path = f"outputs/reports/{base_name}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# Phase 1 HL7 FHIR R4 Interoperability & Mapping Audit Report\n\n")
            f.write(f"- **Run ID:** `{audit_report.run_id}`\n")
            f.write(f"- **Target Database:** `{audit_report.database_name}`\n")
            f.write(f"- **SHA256 Fingerprint:** `{audit_report.database_checksum_sha256}`\n")
            f.write(f"- **Timestamp:** `{audit_report.timestamp}`\n")
            f.write(f"- **LLM Provider / Model:** `{audit_report.llm_provider}` / `{audit_report.llm_model}`\n")
            f.write(f"- **Accepted Mappings:** {audit_report.accepted_count} | **Review:** {audit_report.review_count} | **Unsupported:** {audit_report.unsupported_count}\n\n")

            f.write(f"## Summary Table\n\n")
            rows = [
                [
                    r.legacy_field,
                    r.semantic_meaning,
                    r.fhir_candidate.target_path if r.fhir_candidate else "(none)",
                    f"{r.confidence_breakdown.mapping_confidence:.2f}",
                    r.confidence_breakdown.evidence_strength,
                    f"**{r.decision.decision}**",
                    f"`{r.decision.rule_id}`",
                ]
                for r in audit_report.field_reports
            ]
            f.write(tabulate(
                rows,
                headers=["Legacy Field", "Semantic Meaning", "FHIR Candidate", "Confidence", "Evidence", "Decision", "Rule"],
                tablefmt="github",
            ))
            f.write("\n\n## Detailed Field Evidence & Provenance\n\n")

            for item in audit_report.field_reports:
                f.write(f"### Field: `{item.legacy_field}`\n\n")
                f.write(f"- **Semantic Meaning:** {item.semantic_meaning}\n")
                f.write(f"- **FHIR Candidate:** `{item.fhir_candidate.target_path if item.fhir_candidate else 'None'}`\n")
                f.write(f"- **Decision:** **{item.decision.decision}** (Rule: `{item.decision.rule_id}`)\n")
                f.write(f"- **Decision Reason:** {item.decision.reason}\n")
                f.write(f"- **Mapping Confidence:** `{item.confidence_breakdown.mapping_confidence:.2f}` (Evidence Strength: `{item.confidence_breakdown.evidence_strength}`)\n\n")

                f.write(f"#### Observed Facts\n")
                for f_text in item.observed_facts:
                    f.write(f"- {f_text}\n")

                if item.inferred_facts:
                    f.write(f"\n#### Inferred Facts\n")
                    for inf in item.inferred_facts:
                        f.write(f"- {inf}\n")

                f.write(f"\n#### Retrieved Authoritative Evidence\n")
                for ev in item.retrieved_evidence_summary:
                    f.write(f"- {ev}\n")

                f.write(f"\n#### Provenance & Audit Trail\n")
                for p in item.provenance:
                    f.write(f"- {p}\n")
                f.write("\n---\n\n")

        print(f"Persisted Markdown:     {md_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Phase 1 Legacy EHR to FHIR R4 Interoperability Pipeline.")
    parser.add_argument("--db", type=str, default="data/hospital_a.db", help="Path to legacy SQLite database")
    parser.add_argument("--provider", type=str, default=None, help="LLM provider: groq, openrouter, mock, gemini")
    parser.add_argument("--model", type=str, default=None, help="Specific model name")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of fields to process")
    args = parser.parse_args()

    pipeline = Phase1Pipeline(provider_name=args.provider, model_name=args.model)
    pipeline.run(db_path=args.db, limit=args.limit)
