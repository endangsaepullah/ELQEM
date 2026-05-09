import streamlit as st
import os

st.set_page_config(
    page_title="IQLE Platform | PT Pindad",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    :root {
        --primary-color: #00d4ff;
        --background-color: #070b14;
        --secondary-background-color: #0d1321;
        --text-color: #e8edf5;
    }
</style>
""", unsafe_allow_html=True)

os.makedirs("data", exist_ok=True)

from utils.database import init_database
from utils.auth import create_default_admin, login_page, logout, is_admin
from utils.seed_data import seed_dummy_data
from utils.styles import apply_global_style

init_database()
create_default_admin()
seed_dummy_data()
apply_global_style()

# ── Auth gate ──────────────────────────────────────────────
if not st.session_state.get('logged_in'):
    login_page()
    st.stop()

user = st.session_state.get('user', {})
role = st.session_state.get('role', 'viewer')

# ── Sidebar ────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding:1rem 0 1.5rem;
                border-bottom:1px solid rgba(0,212,255,0.15); margin-bottom:1rem;">
        <div style="font-size:2.2rem;">⚙️</div>
        <div style="font-family:'Rajdhani',sans-serif; font-size:1.15rem; font-weight:700;
                    color:#00d4ff; letter-spacing:2px;">IQLE PLATFORM</div>
        <div style="font-size:0.62rem; color:#4a6fa5; letter-spacing:3px;
                    text-transform:uppercase;">PT Pindad (Persero)</div>
    </div>
    <div style="padding:0.65rem 0.85rem; margin-bottom:1rem;
                background:rgba(0,212,255,0.05); border:1px solid rgba(0,212,255,0.15);
                border-radius:8px;">
        <div style="font-size:0.65rem; color:#4a6fa5; letter-spacing:1px;
                    text-transform:uppercase;">Logged in as</div>
        <div style="font-family:'Rajdhani',sans-serif; font-size:0.95rem;
                    font-weight:600; color:#e8edf5;">
            {user.get('full_name') or user.get('username','User')}
        </div>
        <div style="font-size:0.68rem; letter-spacing:1px; text-transform:uppercase;
                    color:{'#00d4ff' if role=='admin' else '#ffd700'};">
            {'🔑 ADMIN' if role=='admin' else '👁 VIEWER'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if 'page' not in st.session_state:
        st.session_state.page = 'home'

    menu = [
        ("🏠 Dashboard Utama",         "home"),
        ("📊 ISO 9001",                "iso9001"),
        ("🏭 IATF 16949",              "iatf"),
        ("⚙️ Engineering Lifecycle",   "lifecycle"),
        ("✅ Konsistensi Mutu",         "consistency"),
        ("📦 Evaluasi Batch",           "batch"),
        ("🎯 Integrated Quality Score", "iqscore"),
        ("💬 Data Wawancara",           "interview"),
        ("👥 Manajemen User",           "users"),
    ]

    for label, pid in menu:
        if pid == "users" and not is_admin():
            continue
        active = st.session_state.page == pid
        if st.button(label, key=f"nav_{pid}", use_container_width=True,
                     type="primary" if active else "secondary"):
            st.session_state.page = pid
            st.rerun()

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        logout()

# ── Page routing ───────────────────────────────────────────
p = st.session_state.page

if p == "home":
    from modules.pg_home import show
elif p == "iso9001":
    from modules.pg_iso9001 import show
elif p == "iatf":
    from modules.pg_iatf import show
elif p == "lifecycle":
    from modules.pg_lifecycle import show
elif p == "consistency":
    from modules.pg_consistency import show
elif p == "batch":
    from modules.pg_batch import show
elif p == "iqscore":
    from modules.pg_iqscore import show
elif p == "interview":
    from modules.pg_interview import show
elif p == "users":
    from modules.pg_users import show
else:
    from modules.pg_home import show

show()
