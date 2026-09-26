import json

with open("outputs/profiles/hospital_a.db_profile.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"DATABASE: {data['database_name']} (SHA256: {data['checksum_sha256']})")
print(f"Total Tables: {data['summary']['total_tables']}, Total Columns: {data['summary']['total_columns']}, Total Rows: {data['summary']['total_rows']}")
print("\n" + "="*80)

for tbl_name, tbl in data["tables"].items():
    print(f"\nTABLE: {tbl_name} ({tbl['row_count']:,} rows, {tbl['column_count']} columns)")
    print(f"  Declared PK: {tbl['declared_primary_keys']}")
    print(f"  Candidate PK: {tbl['candidate_primary_keys']}")
    print(f"  Declared FK: {tbl['declared_foreign_keys']}")
    print("  COLUMNS:")
    for col_name, c in tbl["columns"].items():
        sample_str = ", ".join(repr(s) for s in c["sample_values"][:3])
        print(f"    - {col_name:22} | {c['data_type']:8} | Nulls: {c['null_count']:5} ({c['null_percentage']}%) | Distinct: {c['distinct_count']:5} ({c['uniqueness_ratio']:.1%}) | Samples: [{sample_str}]")
