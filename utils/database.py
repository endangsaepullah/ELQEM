"""
database.py — Turso via HTTP API (requests only, no special library needed)
Data persisten permanen di Turso cloud.
"""
import os
import requests


def _creds():
    try:
        import streamlit as st
        return st.secrets["TURSO_URL"], st.secrets["TURSO_TOKEN"]
    except Exception:
        return os.environ.get("TURSO_URL",""), os.environ.get("TURSO_TOKEN","")


def _execute(statements):
    """
    Kirim satu atau beberapa SQL statement ke Turso HTTP API.
    statements: list of {"q": "SQL", "params": [...]} atau str
    Return: list of result sets
    """
    url, token = _creds()
    if not url or not token:
        raise ValueError("TURSO_URL / TURSO_TOKEN tidak ada di Secrets.")

    # Normalise
    reqs = []
    for s in statements:
        if isinstance(s, str):
            reqs.append({"q": s, "params": []})
        elif isinstance(s, dict):
            reqs.append({"q": s["q"], "params": s.get("params", [])})

    endpoint = url.rstrip("/").replace("libsql://", "https://") + "/v2/pipeline"
    body = {"requests": [{"type": "execute", "stmt": r} for r in reqs]
            + [{"type": "close"}]}

    resp = requests.post(
        endpoint,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=body,
        timeout=15
    )
    resp.raise_for_status()
    return resp.json().get("results", [])


def _q(sql, params=None):
    """Single query helper — return raw result."""
    stmt = {"q": sql, "params": _to_turso_params(params or [])}
    results = _execute([stmt])
    return results[0] if results else {}


def _to_turso_params(params):
    """Convert Python values to Turso param format."""
    out = []
    for p in params:
        if p is None:
            out.append({"type": "null", "value": None})
        elif isinstance(p, bool):
            out.append({"type": "integer", "value": str(int(p))})
        elif isinstance(p, int):
            out.append({"type": "integer", "value": str(p)})
        elif isinstance(p, float):
            out.append({"type": "float", "value": str(p)})
        elif isinstance(p, (bytes, bytearray)):
            import base64
            out.append({"type": "blob", "value": base64.b64encode(p).decode()})
        else:
            out.append({"type": "text", "value": str(p)})
    return out


def _parse_rows(result):
    """Parse Turso result into list of dicts."""
    try:
        res = result.get("response", {}).get("result", {})
        cols = [c["name"] for c in res.get("cols", [])]
        rows = []
        for row in res.get("rows", []):
            d = {}
            for i, col in enumerate(cols):
                cell = row[i]
                t = cell.get("type", "null")
                v = cell.get("value")
                if t == "null":   d[col] = None
                elif t == "integer": d[col] = int(v) if v is not None else None
                elif t == "float":   d[col] = float(v) if v is not None else None
                elif t == "blob":
                    import base64
                    d[col] = base64.b64decode(v) if v else None
                else:             d[col] = v
            rows.append(d)
        return rows
    except Exception:
        return []


# ── Public API ─────────────────────────────────────────────

def fetchall(sql, params=None):
    result = _q(sql, params or [])
    return _parse_rows(result)


def fetchone(sql, params=None):
    rows = fetchall(sql, params)
    return rows[0] if rows else None


def execute(sql, params=None):
    _q(sql, params or [])


def executemany(statements):
    """statements: list of (sql, params) tuples"""
    stmts = [{"q": s, "params": _to_turso_params(p or [])} for s, p in statements]
    _execute(stmts)


def init_database():
    tables = [
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT, role TEXT NOT NULL DEFAULT 'viewer',
            email TEXT, is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')), last_login TEXT)""",
        """CREATE TABLE IF NOT EXISTS batch_production (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_number TEXT UNIQUE NOT NULL, production_date TEXT NOT NULL,
            vehicle_type TEXT DEFAULT 'Kendaraan Multifungsi Nasional',
            total_units INTEGER DEFAULT 0, total_defect INTEGER DEFAULT 0,
            total_rework INTEGER DEFAULT 0, defect_rate REAL DEFAULT 0.0,
            rework_rate REAL DEFAULT 0.0, pic TEXT,
            status TEXT DEFAULT 'In Progress', notes TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')))""",
        """CREATE TABLE IF NOT EXISTS defect_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id INTEGER, batch_number TEXT,
            defect_type TEXT NOT NULL, defect_stage TEXT NOT NULL,
            quantity INTEGER DEFAULT 1, root_cause TEXT,
            corrective_action TEXT, pic TEXT,
            follow_up_status TEXT DEFAULT 'Open',
            found_date TEXT, resolved_date TEXT,
            created_at TEXT DEFAULT (datetime('now')))""",
        """CREATE TABLE IF NOT EXISTS iso9001_evaluation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            eval_date TEXT NOT NULL, batch_number TEXT,
            process_documentation REAL DEFAULT 0, process_control REAL DEFAULT 0,
            internal_audit REAL DEFAULT 0, corrective_action REAL DEFAULT 0,
            continuous_improvement REAL DEFAULT 0, average_score REAL DEFAULT 0,
            category TEXT, evaluator TEXT, notes TEXT,
            created_at TEXT DEFAULT (datetime('now')))""",
        """CREATE TABLE IF NOT EXISTS iatf16949_evaluation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            eval_date TEXT NOT NULL, batch_number TEXT,
            risk_based_thinking REAL DEFAULT 0, defect_prevention REAL DEFAULT 0,
            supplier_quality REAL DEFAULT 0, continuous_improvement REAL DEFAULT 0,
            average_score REAL DEFAULT 0, category TEXT, evaluator TEXT, notes TEXT,
            created_at TEXT DEFAULT (datetime('now')))""",
        """CREATE TABLE IF NOT EXISTS engineering_lifecycle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            eval_date TEXT NOT NULL, batch_number TEXT,
            design_control REAL DEFAULT 0, change_control REAL DEFAULT 0,
            verification_validation REAL DEFAULT 0, integration_process REAL DEFAULT 0,
            traceability REAL DEFAULT 0, design_change_communication REAL DEFAULT 0,
            average_score REAL DEFAULT 0, maturity_level TEXT,
            evaluator TEXT, notes TEXT,
            created_at TEXT DEFAULT (datetime('now')))""",
        """CREATE TABLE IF NOT EXISTS quality_consistency (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            eval_date TEXT NOT NULL, batch_number TEXT,
            quality_uniformity REAL DEFAULT 0, low_defect_rate REAL DEFAULT 0,
            inter_batch_stability REAL DEFAULT 0, low_rework_rate REAL DEFAULT 0,
            spec_conformance REAL DEFAULT 0, average_score REAL DEFAULT 0,
            category TEXT, evaluator TEXT, notes TEXT,
            created_at TEXT DEFAULT (datetime('now')))""",
        """CREATE TABLE IF NOT EXISTS interview_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_date TEXT NOT NULL, informant_name TEXT NOT NULL,
            position TEXT, work_unit TEXT, interview_result TEXT,
            key_insights TEXT, finding_category TEXT, interviewer TEXT,
            created_at TEXT DEFAULT (datetime('now')))""",
        """CREATE TABLE IF NOT EXISTS about_platform (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL, value TEXT,
            updated_at TEXT DEFAULT (datetime('now')))""",
        """CREATE TABLE IF NOT EXISTS about_photo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT, photo_data TEXT,
            mime_type TEXT DEFAULT 'image/jpeg',
            uploaded_at TEXT DEFAULT (datetime('now')))""",
        """CREATE TABLE IF NOT EXISTS login_logo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT, logo_data TEXT,
            mime_type TEXT DEFAULT 'image/png',
            uploaded_at TEXT DEFAULT (datetime('now')))""",
    ]
    _execute(tables)


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
