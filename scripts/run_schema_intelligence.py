"""
Run Schema Intelligence Agent across tables and columns in a database profile.
Displays semantic role, candidate terminology, confidence, observed facts vs inferences.
Usage:
    python scripts/run_schema_intelligence.py [--profile outputs/profiles/hospital_a.db_profile.json] [--limit 10]
"""

import os
import sys
import json
import argparse
from tabulate import tabulate

# Force UTF-8 stdout encoding on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.schemas import DatabaseProfile, SchemaIntelligenceResult
from models.llm_provider import LLMProvider
from agents.schema_intelligence import SchemaIntelligenceAgent


def run_schema_intelligence(profile_path: str, limit: int = 15, provider_name: str = None):
    print(f"\n{'='*80}")
    print(f"SCHEMA INTELLIGENCE AGENT (MODULE 2) — CLINICAL ROLE & TERMINOLOGY INFERENCE")
    print(f"{'='*80}")

    with open(profile_path, "r", encoding="utf-8") as f:
        profile_data = json.load(f)

    db_profile = DatabaseProfile.model_validate(profile_data)
    print(f"Loaded Profile: {db_profile.database_name} ({db_profile.summary['total_tables']} tables, {db_profile.summary['total_columns']} columns)")

    # Initialize agent
    llm = LLMProvider(provider=provider_name) if provider_name else LLMProvider()
    print(f"Using LLM Provider: {llm.provider} (Model: {llm.model})")

    agent = SchemaIntelligenceAgent(llm_provider=llm)

    results: list[SchemaIntelligenceResult] = []
    table_rows = []

    count = 0
    for tbl_name, tbl_prof in db_profile.tables.items():
        for col_name, col_fact in tbl_prof.columns.items():
            if limit and count >= limit:
                break

            print(f"  Analyzing {tbl_name}.{col_name}...", end=" ", flush=True)
            res = agent.analyze_column(col_fact, tbl_prof, db_profile.observed_value_overlaps)
            results.append(res)
            print(f"-> {res.role.role_category} ({res.role.candidate_terminology}) [{res.role.confidence:.2f}]")

            table_rows.append([
                f"{tbl_name}.{col_name}",
                res.role.role_category,
                res.role.candidate_terminology or "NONE",
                f"{res.role.confidence:.2f}",
                res.role.semantic_meaning,
                "; ".join(res.role.inferred_facts[:2]) if res.role.inferred_facts else "-",
            ])
            count += 1
        if limit and count >= limit:
            break

    print(f"\n[RESULTS TABLE]")
    print(tabulate(
        table_rows,
        headers=["Field", "Semantic Role", "Terminology", "Conf", "Semantic Meaning", "Inferred Rationale"],
        tablefmt="github"
    ))

    # Persist results
    os.makedirs("outputs/intelligence", exist_ok=True)
    out_path = f"outputs/intelligence/{db_profile.database_name}_intelligence.json"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(json.dumps([r.model_dump() for r in results], indent=2))
    print(f"\nPersisted intelligence results to: {out_path}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="outputs/profiles/hospital_a.db_profile.json")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--provider", type=str, default=None)
    args = parser.parse_args()

    run_schema_intelligence(args.profile, limit=args.limit, provider_name=args.provider)
