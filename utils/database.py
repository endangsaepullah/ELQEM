"""
database.py — SQLite dengan st.cache_resource
Data bertahan selama app running (tidak hilang saat sleep).
Hanya reset saat deploy ulang ke GitHub.
"""
import sqlite3
import os
import streamlit as st

DB_PATH = "/tmp/pindad_quality.db"


@st.cache_resource
def _get_cached_connection():
    """Koneksi SQLite yang di-cache — tidak hilang saat sleep."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def get_connection():
    return _get_cached_connection()


def init_database():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        role TEXT NOT NULL DEFAULT 'viewer',
        email TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now')),
        last_login TEXT
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS batch_production (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS defect_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        created_at TEXT DEFAULT (datetime('now'))
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS iso9001_evaluation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        created_at TEXT DEFAULT (datetime('now'))
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS iatf16949_evaluation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        created_at TEXT DEFAULT (datetime('now'))
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS engineering_lifecycle (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        created_at TEXT DEFAULT (datetime('now'))
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS quality_consistency (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        created_at TEXT DEFAULT (datetime('now'))
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS interview_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interview_date TEXT NOT NULL,
        informant_name TEXT NOT NULL,
        position TEXT,
        work_unit TEXT,
        interview_result TEXT,
        key_insights TEXT,
        finding_category TEXT,
        interviewer TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS about_platform (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        value TEXT,
        updated_at TEXT DEFAULT (datetime('now'))
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS about_photo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        photo_data BLOB,
        mime_type TEXT DEFAULT 'image/jpeg',
        uploaded_at TEXT DEFAULT (datetime('now'))
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS login_logo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        logo_data BLOB,
        mime_type TEXT DEFAULT 'image/png',
        uploaded_at TEXT DEFAULT (datetime('now'))
    )""")

    conn.commit()


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
