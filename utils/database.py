"""
database.py — koneksi ke Supabase PostgreSQL
Persistent: data tidak hilang saat Streamlit Cloud restart.
"""
import os
import psycopg2
import psycopg2.extras
from contextlib import contextmanager

# ── Connection ─────────────────────────────────────────────
def _get_db_url():
    """Ambil DATABASE_URL dari Streamlit secrets atau env."""
    try:
        import streamlit as st
        return st.secrets["DATABASE_URL"]
    except Exception:
        return os.environ.get(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/postgres"
        )

def get_connection():
    url = _get_db_url()
    conn = psycopg2.connect(url, cursor_factory=psycopg2.extras.RealDictCursor)
    conn.autocommit = False
    return conn

# ── Init schema ────────────────────────────────────────────
def init_database():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        role TEXT NOT NULL DEFAULT 'viewer',
        email TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (to_char(now(),'YYYY-MM-DD HH24:MI:SS')),
        last_login TEXT
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS batch_production (
        id SERIAL PRIMARY KEY,
        batch_number TEXT UNIQUE NOT NULL,
        production_date TEXT NOT NULL,
        vehicle_type TEXT DEFAULT 'Kendaraan Multifungsi Nasional',
        total_units INTEGER DEFAULT 0,
        total_defect INTEGER DEFAULT 0,
        total_rework INTEGER DEFAULT 0,
        defect_rate REAL DEFAULT 0.0,
        rework_rate REAL DEFAULT 0.0,
        pic TEXT,
        status TEXT DEFAULT 'In Progress',
        notes TEXT,
        created_at TEXT DEFAULT (to_char(now(),'YYYY-MM-DD HH24:MI:SS')),
        updated_at TEXT DEFAULT (to_char(now(),'YYYY-MM-DD HH24:MI:SS'))
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS defect_records (
        id SERIAL PRIMARY KEY,
        batch_id INTEGER REFERENCES batch_production(id),
        batch_number TEXT,
        defect_type TEXT NOT NULL,
        defect_stage TEXT NOT NULL,
        quantity INTEGER DEFAULT 1,
        root_cause TEXT,
        corrective_action TEXT,
        pic TEXT,
        follow_up_status TEXT DEFAULT 'Open',
        found_date TEXT,
        resolved_date TEXT,
        created_at TEXT DEFAULT (to_char(now(),'YYYY-MM-DD HH24:MI:SS'))
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS iso9001_evaluation (
        id SERIAL PRIMARY KEY,
        eval_date TEXT NOT NULL,
        batch_number TEXT,
        process_documentation REAL DEFAULT 0,
        process_control REAL DEFAULT 0,
        internal_audit REAL DEFAULT 0,
        corrective_action REAL DEFAULT 0,
        continuous_improvement REAL DEFAULT 0,
        average_score REAL DEFAULT 0,
        category TEXT,
        evaluator TEXT,
        notes TEXT,
        created_at TEXT DEFAULT (to_char(now(),'YYYY-MM-DD HH24:MI:SS'))
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS iatf16949_evaluation (
        id SERIAL PRIMARY KEY,
        eval_date TEXT NOT NULL,
        batch_number TEXT,
        risk_based_thinking REAL DEFAULT 0,
        defect_prevention REAL DEFAULT 0,
        supplier_quality REAL DEFAULT 0,
        continuous_improvement REAL DEFAULT 0,
        average_score REAL DEFAULT 0,
        category TEXT,
        evaluator TEXT,
        notes TEXT,
        created_at TEXT DEFAULT (to_char(now(),'YYYY-MM-DD HH24:MI:SS'))
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS engineering_lifecycle (
        id SERIAL PRIMARY KEY,
        eval_date TEXT NOT NULL,
        batch_number TEXT,
        design_control REAL DEFAULT 0,
        change_control REAL DEFAULT 0,
        verification_validation REAL DEFAULT 0,
        integration_process REAL DEFAULT 0,
        traceability REAL DEFAULT 0,
        design_change_communication REAL DEFAULT 0,
        average_score REAL DEFAULT 0,
        maturity_level TEXT,
        evaluator TEXT,
        notes TEXT,
        created_at TEXT DEFAULT (to_char(now(),'YYYY-MM-DD HH24:MI:SS'))
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS quality_consistency (
        id SERIAL PRIMARY KEY,
        eval_date TEXT NOT NULL,
        batch_number TEXT,
        quality_uniformity REAL DEFAULT 0,
        low_defect_rate REAL DEFAULT 0,
        inter_batch_stability REAL DEFAULT 0,
        low_rework_rate REAL DEFAULT 0,
        spec_conformance REAL DEFAULT 0,
        average_score REAL DEFAULT 0,
        category TEXT,
        evaluator TEXT,
        notes TEXT,
        created_at TEXT DEFAULT (to_char(now(),'YYYY-MM-DD HH24:MI:SS'))
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS interview_data (
        id SERIAL PRIMARY KEY,
        interview_date TEXT NOT NULL,
        informant_name TEXT NOT NULL,
        position TEXT,
        work_unit TEXT,
        interview_result TEXT,
        key_insights TEXT,
        finding_category TEXT,
        interviewer TEXT,
        created_at TEXT DEFAULT (to_char(now(),'YYYY-MM-DD HH24:MI:SS'))
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS about_platform (
        id SERIAL PRIMARY KEY,
        key TEXT UNIQUE NOT NULL,
        value TEXT,
        updated_at TEXT DEFAULT (to_char(now(),'YYYY-MM-DD HH24:MI:SS'))
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS about_photo (
        id SERIAL PRIMARY KEY,
        filename TEXT,
        photo_data BYTEA,
        mime_type TEXT DEFAULT 'image/jpeg',
        uploaded_at TEXT DEFAULT (to_char(now(),'YYYY-MM-DD HH24:MI:SS'))
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS login_logo (
        id SERIAL PRIMARY KEY,
        filename TEXT,
        logo_data BYTEA,
        mime_type TEXT DEFAULT 'image/png',
        uploaded_at TEXT DEFAULT (to_char(now(),'YYYY-MM-DD HH24:MI:SS'))
    )""")

    conn.commit()
    c.close()
    conn.close()


def get_category(score):
    if score >= 85:   return "Sangat Baik"
    elif score >= 75: return "Baik"
    elif score >= 60: return "Cukup"
    else:             return "Perlu Perbaikan"


def get_lifecycle_maturity(score):
    if score >= 85:   return "Optimized"
    elif score >= 75: return "Managed"
    elif score >= 60: return "Defined"
    elif score >= 40: return "Developing"
    else:             return "Initial"
