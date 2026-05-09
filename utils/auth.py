import streamlit as st
import hashlib
from utils.database import get_connection
from datetime import datetime


def hash_password(password: str) -> str:
    """Hash password menggunakan SHA-256 (stdlib, no extra deps)."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed


def create_default_admin():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = 'admin'")
    if not c.fetchone():
        c.execute("""
            INSERT INTO users (username, password_hash, full_name, role, email, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('admin', hash_password('admin123'), 'Administrator', 'admin', 'admin@pindad.com', 1))
        conn.commit()
    conn.close()


def authenticate(username: str, password: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (username,))
    user = c.fetchone()
    if user and verify_password(password, user['password_hash']):
        c.execute("UPDATE users SET last_login = ? WHERE id = ?",
                  (datetime.now().isoformat(), user['id']))
        conn.commit()
        conn.close()
        return dict(user)
    conn.close()
    return None


def login_page():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=Inter:wght@400;500&display=swap');
    .stApp { background: #070b14; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; margin-bottom:2rem;">
            <div style="font-size:3.5rem;">⚙️</div>
            <div style="font-family:'Rajdhani',sans-serif; font-size:1.8rem; font-weight:700;
                        color:#00d4ff; letter-spacing:3px;">IQLE PLATFORM</div>
            <div style="font-size:0.7rem; color:#4a6fa5; letter-spacing:3px;
                        text-transform:uppercase; margin-top:4px;">PT Pindad (Persero) · Quality 4.0</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Masukkan username")
            password = st.text_input("🔒 Password", type="password", placeholder="Masukkan password")
            submitted = st.form_submit_button("🚀 LOGIN", use_container_width=True, type="primary")

            if submitted:
                if username and password:
                    user = authenticate(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.role = user['role']
                        st.rerun()
                    else:
                        st.error("❌ Username atau password salah.")
                else:
                    st.warning("⚠️ Harap isi username dan password.")

        st.markdown("""
        <div style="text-align:center; margin-top:1rem; font-size:0.75rem; color:#3d5470;">
            Default: admin / admin123
        </div>
        """, unsafe_allow_html=True)


def logout():
    for key in ['logged_in', 'user', 'role']:
        st.session_state.pop(key, None)
    st.rerun()


def is_admin():
    return st.session_state.get('role') == 'admin'


def require_admin():
    if not is_admin():
        st.error("⛔ Akses ditolak. Fitur ini hanya untuk Admin.")
        st.stop()
