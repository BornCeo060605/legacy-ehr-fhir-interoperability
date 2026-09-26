"""
Unit tests for Deterministic Schema Profiler.
Tests profiling accuracy, edge cases (empty table, nulls), and read-only enforcement.
"""

import os
import sqlite3
import pytest
from tools.schema_profiler import SchemaProfiler
from models.schemas import DatabaseProfile


@pytest.fixture
def temp_test_db(tmp_path):
    """Create a temporary test database with diverse columns, nulls, and relationships."""
    db_file = tmp_path / "test_legacy.db"
    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()

    # Table 1: PATIENT_MASTER
    cur.execute("""
        CREATE TABLE PATIENT_MASTER (
            PAT_ID TEXT PRIMARY KEY,
            NAME TEXT NOT NULL,
            BIRTH_DATE TEXT,
            STATUS_CODE INTEGER
        )
    """)
    cur.executemany("""
        INSERT INTO PATIENT_MASTER VALUES (?, ?, ?, ?)
    """, [
        ("P001", "Alice Smith", "1980-05-12", 1),
        ("P002", "Bob Jones", "1992-11-23", 1),
        ("P003", "Charlie Brown", "1975-01-30", 2),
    ])

    # Table 2: ENCOUNTERS with foreign key
    cur.execute("""
        CREATE TABLE ENCOUNTERS (
            ENC_ID TEXT PRIMARY KEY,
            PAT_ID TEXT NOT NULL,
            ENC_DATE TEXT,
            FOREIGN KEY (PAT_ID) REFERENCES PATIENT_MASTER(PAT_ID)
        )
    """)
    cur.executemany("""
        INSERT INTO ENCOUNTERS VALUES (?, ?, ?)
    """, [
        ("E101", "P001", "2023-01-10"),
        ("E102", "P002", "2023-02-15"),
    ])

    # Table 3: LAB_RESULTS with value overlap but undeclared FK, plus nulls
    cur.execute("""
        CREATE TABLE LAB_RESULTS (
            LAB_ID TEXT,
            PID TEXT,
            TEST_CODE TEXT,
            NUM_VAL REAL,
            UNIT TEXT,
            NOTES TEXT
        )
    """)
    cur.executemany("""
        INSERT INTO LAB_RESULTS VALUES (?, ?, ?, ?, ?, ?)
    """, [
        ("L001", "P001", "2345-7", 120.5, "mg/dL", None),
        ("L002", "P002", "2345-7", 135.0, "mg/dL", "Fasting"),
        ("L003", "P003", "718-7", 14.2, "g/dL", None),
    ])

    # Table 4: EMPTY_TABLE (Edge case)
    cur.execute("""
        CREATE TABLE EMPTY_TABLE (
            ID TEXT,
            DATA TEXT
        )
    """)

    conn.commit()
    conn.close()
    return str(db_file)


def test_schema_profiler_basic(temp_test_db):
    """Test standard profiling on multi-table database."""
    profiler = SchemaProfiler(temp_test_db)
    profile = profiler.profile_database()

    assert isinstance(profile, DatabaseProfile)
    assert profile.summary["total_tables"] == 4
    assert len(profile.checksum_sha256) == 64

    # Check PATIENT_MASTER
    pm = profile.tables["PATIENT_MASTER"]
    assert pm.row_count == 3
    assert "PAT_ID" in pm.declared_primary_keys
    assert "PAT_ID" in pm.candidate_primary_keys
    assert pm.columns["PAT_ID"].is_unique is True
    assert pm.columns["PAT_ID"].distinct_count == 3
    assert pm.columns["PAT_ID"].null_count == 0

    # Date detection
    assert pm.columns["BIRTH_DATE"].date_stats is not None
    assert pm.columns["BIRTH_DATE"].date_stats.likely_format == "%Y-%m-%d"

    # Numeric stats on LAB_RESULTS.NUM_VAL
    lab = profile.tables["LAB_RESULTS"]
    assert lab.row_count == 3
    val_col = lab.columns["NUM_VAL"]
    assert val_col.numeric_stats is not None
    assert val_col.numeric_stats.min == 14.2
    assert val_col.numeric_stats.max == 135.0

    # Check null stats on LAB_RESULTS.NOTES
    notes_col = lab.columns["NOTES"]
    assert notes_col.null_count == 2
    assert notes_col.non_null_count == 1
    assert notes_col.null_percentage > 60.0


def test_declared_and_overlap_relationships(temp_test_db):
    """Test declared foreign keys and observed value overlap detection."""
    profiler = SchemaProfiler(temp_test_db)
    profile = profiler.profile_database()

    # Declared FK in ENCOUNTERS
    assert len(profile.declared_foreign_keys) == 1
    fk = profile.declared_foreign_keys[0]
    assert fk["source_table"] == "ENCOUNTERS"
    assert fk["from_column"] == "PAT_ID"
    assert fk["target_table"] == "PATIENT_MASTER"
    assert fk["target_column"] == "PAT_ID"

    # Discovered overlap between LAB_RESULTS.PID and PATIENT_MASTER.PAT_ID
    # PID has P001, P002, P003 which are 100% in PATIENT_MASTER.PAT_ID
    overlaps = [
        r for r in profile.observed_value_overlaps
        if r.source_table == "LAB_RESULTS" and r.source_column == "PID"
        and r.target_table == "PATIENT_MASTER" and r.target_column == "PAT_ID"
    ]
    assert len(overlaps) == 1
    overlap_rel = overlaps[0]
    assert overlap_rel.overlap_count == 3
    assert overlap_rel.source_containment == 1.0
    assert "Consistent with a foreign-key" in overlap_rel.inference


def test_empty_table_edge_case(temp_test_db):
    """Test profiling on an empty table."""
    profiler = SchemaProfiler(temp_test_db)
    profile = profiler.profile_database()

    empty_tbl = profile.tables["EMPTY_TABLE"]
    assert empty_tbl.row_count == 0
    assert empty_tbl.columns["ID"].null_count == 0
    assert empty_tbl.columns["ID"].non_null_count == 0
    assert empty_tbl.columns["ID"].distinct_count == 0
    assert empty_tbl.columns["ID"].is_unique is False
