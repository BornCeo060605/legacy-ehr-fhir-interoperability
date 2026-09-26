"""
Script to profile a legacy EHR database deterministically and display rich summary tables.
Usage:
    python scripts/profile_database.py [--db data/hospital_a.db]
"""

import os
import sys
import json
import argparse
from tabulate import tabulate

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.schema_profiler import SchemaProfiler


def run_profiler(db_path: str, output_json: bool = True):
    print(f"\n{'='*80}")
    print(f"DETERMINISTIC SCHEMA PROFILER — HL7 FHIR R4 INTEROPERABILITY PIPELINE")
    print(f"{'='*80}")
    print(f"Target Database: {db_path}")

    profiler = SchemaProfiler(db_path)
    profile = profiler.profile_database()

    print(f"\n[1] DATABASE METADATA & INTEGRITY")
    print(f"  - Database Name:      {profile.database_name}")
    print(f"  - Absolute Path:      {profile.database_path}")
    print(f"  - SHA256 Checksum:    {profile.checksum_sha256}")
    print(f"  - Profiling Time:     {profile.profiling_timestamp}")
    print(f"  - Total Tables:       {profile.summary['total_tables']}")
    print(f"  - Total Columns:      {profile.summary['total_columns']}")
    print(f"  - Total Rows:         {profile.summary['total_rows']}")
    print(f"  - Declared FKs:       {profile.summary['declared_fk_count']}")
    print(f"  - Discovered Overlaps:{profile.summary['discovered_overlap_count']}")

    print(f"\n[2] TABLE SUMMARY")
    table_summary_rows = []
    for tbl_name, tbl_prof in profile.tables.items():
        table_summary_rows.append([
            tbl_name,
            f"{tbl_prof.row_count:,}",
            tbl_prof.column_count,
            ", ".join(tbl_prof.declared_primary_keys) if tbl_prof.declared_primary_keys else "NONE",
            ", ".join(tbl_prof.candidate_primary_keys) if tbl_prof.candidate_primary_keys else "NONE",
            len(tbl_prof.declared_foreign_keys),
        ])
    print(tabulate(
        table_summary_rows,
        headers=["Table Name", "Row Count", "Columns", "Declared PK", "Candidate PK", "Declared FKs"],
        tablefmt="github"
    ))

    print(f"\n[3] COLUMN-LEVEL DETAILED PROFILE")
    for tbl_name, tbl_prof in profile.tables.items():
        print(f"\n>>> Table: {tbl_name} ({tbl_prof.row_count:,} rows)")
        col_rows = []
        for col_name, c in tbl_prof.columns.items():
            # Format sample values
            samples_str = ", ".join(f"'{s}'" for s in c.sample_values[:3])
            if len(c.sample_values) > 3:
                samples_str += ", ..."
            
            # Format stats
            extra_stats = []
            if c.is_declared_pk:
                extra_stats.append("[PK]")
            elif c.is_unique:
                extra_stats.append("[UNIQUE]")
            if c.date_stats and c.date_stats.likely_format:
                extra_stats.append(f"Date({c.date_stats.likely_format})")
            if c.numeric_stats and c.numeric_stats.min is not None:
                extra_stats.append(f"Num[{c.numeric_stats.min:g}..{c.numeric_stats.max:g}]")

            col_rows.append([
                col_name,
                c.data_type,
                "YES" if c.is_nullable else "NO",
                f"{c.null_count} ({c.null_percentage:.1f}%)",
                f"{c.distinct_count} ({c.uniqueness_ratio:.1%})",
                " | ".join(extra_stats) if extra_stats else "-",
                samples_str if samples_str else "(empty)"
            ])
        print(tabulate(
            col_rows,
            headers=["Column", "Type", "Nullable", "Null Count (%)", "Distinct (%)", "Characteristics", "Sample Values"],
            tablefmt="github"
        ))

    print(f"\n[4] DECLARED FOREIGN KEYS (PRAGMA foreign_key_list)")
    if profile.declared_foreign_keys:
        fk_rows = [
            [fk["source_table"], fk["from_column"], fk["target_table"], fk["target_column"]]
            for fk in profile.declared_foreign_keys
        ]
        print(tabulate(fk_rows, headers=["Source Table", "Source Column", "Target Table", "Target Column"], tablefmt="github"))
    else:
        print("  * None declared in SQLite schema (characteristic of legacy EHR architectures).")

    print(f"\n[5] CANDIDATE IDENTIFIERS (Unique, Non-null Keys)")
    id_rows = [
        [ci["table_name"], ci["column_name"], "Declared PK" if ci["is_declared_pk"] else "Discovered Candidate PK", ci["row_count"]]
        for ci in profile.candidate_identifiers
    ]
    print(tabulate(id_rows, headers=["Table", "Column", "Status", "Row Count"], tablefmt="github"))

    print(f"\n[6] OBSERVED VALUE-OVERLAP RELATIONSHIPS (Cross-table Data Linkage)")
    if profile.observed_value_overlaps:
        overlap_rows = []
        for r in profile.observed_value_overlaps[:25]:  # Show top 25
            overlap_rows.append([
                f"{r.source_table}.{r.source_column}",
                f"{r.target_table}.{r.target_column}",
                r.overlap_count,
                f"{r.source_containment:.1%}",
                f"{r.target_containment:.1%}",
                f"{r.jaccard_similarity:.2f}",
                r.inference
            ])
        print(tabulate(
            overlap_rows,
            headers=["Source Field", "Target Field", "Overlap", "Src Contain", "Tgt Contain", "Jaccard", "Evidence Inference"],
            tablefmt="github"
        ))
    else:
        print("  * No significant cross-table value overlaps discovered.")

    # Save to JSON
    if output_json:
        os.makedirs("outputs/profiles", exist_ok=True)
        out_file = f"outputs/profiles/{profile.database_name}_profile.json"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(profile.model_dump_json(indent=2))
        print(f"\n[7] PROFILER OUTPUT PERSISTED")
        print(f"  - Structured JSON saved to: {out_file}")

    return profile


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Profile Legacy EHR Database deterministically.")
    parser.add_argument("--db", type=str, default="data/hospital_a.db", help="Path to SQLite database")
    args = parser.parse_args()

    run_profiler(args.db)
