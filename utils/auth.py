import streamlit as st
import hashlib
import base64
from utils.database import get_connection
from datetime import datetime


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed


def create_default_admin():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = 'admin'")
    if not c.fetchone():
        conn.execute(
            "INSERT INTO users (username,password_hash,full_name,role,email,is_active)"
            " VALUES (?,?,?,?,?,?)",
            ('admin', hash_password('admin123'), 'Administrator', 'admin', 'admin@pindad.com', 1)
        )
        conn.commit()


def authenticate(username: str, password: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (username,))
    user = c.fetchone()
    if user and verify_password(password, user['password_hash']):
        conn.execute("UPDATE users SET last_login = ? WHERE id = ?",
                     (datetime.now().isoformat(), user['id']))
        conn.commit()
        return dict(user)
    return None


def get_login_logo_b64():
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT logo_data, mime_type FROM login_logo ORDER BY id DESC LIMIT 1")
        row = c.fetchone()
        if row and row['logo_data']:
            b64 = base64.b64encode(row['logo_data']).decode()
            return "data:" + row['mime_type'] + ";base64," + b64
    except Exception:
        pass
    return None


def save_login_logo(file_bytes, mime_type, filename):
    conn = get_connection()
    conn.execute("DELETE FROM login_logo")
    conn.execute(
        "INSERT INTO login_logo (filename,logo_data,mime_type) VALUES (?,?,?)",
        (filename, file_bytes, mime_type)
    )
    conn.commit()


def delete_login_logo():
    conn = get_connection()
    conn.execute("DELETE FROM login_logo")
    conn.commit()


def login_page():
    st.markdown(
        '<style>@import url("https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700'
        '&family=Inter:wght@400;500&display=swap");.stApp{background:#070b14;}</style>',
        unsafe_allow_html=True
    )
    logo_src = get_login_logo_b64()
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        if logo_src:
            st.markdown(
                '<div style="text-align:center;margin-bottom:1.25rem;">'
                '<img src="' + logo_src + '" style="width:120px;height:120px;'
                'object-fit:contain;border-radius:16px;'
                'box-shadow:0 0 32px rgba(0,212,255,0.25);"></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div style="text-align:center;margin-bottom:1.25rem;">'
                '<div style="font-size:3.5rem;">&#9881;&#65039;</div></div>',
                unsafe_allow_html=True
            )
        st.markdown(
            '<div style="text-align:center;margin-bottom:2rem;">'
            '<div style="font-family:Rajdhani,sans-serif;font-size:1.8rem;font-weight:700;'
            'color:#00d4ff;letter-spacing:3px;">IQLE PLATFORM</div>'
            '<div style="font-size:0.7rem;color:#4a6fa5;letter-spacing:3px;'
            'text-transform:uppercase;margin-top:4px;">PT Pindad (Persero) · Quality 4.0</div>'
            '</div>', unsafe_allow_html=True
        )
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Masukkan username")
            password = st.text_input("Password", type="password", placeholder="Masukkan password")
            if st.form_submit_button("LOGIN", use_container_width=True, type="primary"):
                if username and password:
                    user = authenticate(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.role = user['role']
                        st.rerun()
                    else:
                        st.error("Username atau password salah.")
                else:
                    st.warning("Harap isi username dan password.")
        st.markdown(
            '<div style="text-align:center;margin-top:1.25rem;font-family:Rajdhani,sans-serif;'
            'font-size:0.72rem;color:#3d5470;letter-spacing:2px;line-height:1.8;'
            'text-transform:uppercase;">IQLE Platform &nbsp;&bull;&nbsp; Prototype Akademik Magister Teknik'
            '<br>PT Pindad (Persero) &nbsp;&bull;&nbsp; Universitas Pertahanan RI</div>',
            unsafe_allow_html=True
        )


def logout():
    for key in ['logged_in', 'user', 'role']:
        st.session_state.pop(key, None)
    st.rerun()


def is_admin():
    return st.session_state.get('role') == 'admin'


def require_admin():
    if not is_admin():
        st.error("Akses ditolak. Fitur ini hanya untuk Admin.")
        st.stop()
