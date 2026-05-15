import streamlit as st
import pandas as pd
from utils.database import get_connection
from utils.styles import section_header
from utils.auth import require_admin, is_admin, hash_password
from psycopg2 import Binary


def _exec(conn, sql, params=()):
    """Helper: execute write query and commit."""
    c = conn.cursor()
    c.execute(sql, params)
    conn.commit()
    c.close()


def show():
    require_admin()
    section_header("Manajemen User", "Role-Based Access Control", "👥")
    tab1, tab2 = st.tabs(["👤 Daftar User", "➕ Tambah User"])

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id,username,full_name,role,email,is_active,created_at,last_login FROM users ORDER BY id")
    rows = c.fetchall()
    c.close()

    current_user = st.session_state.get("user", {})

    with tab1:
        for row in rows:
            rc = "#00d4ff" if row["role"] == "admin" else "#ffd700"
            ac = "#00ff88" if row["is_active"] else "#ff3366"
            with st.expander(
                ("🔑 " if row["role"] == "admin" else "👁 ")
                + (row["full_name"] or row["username"])
                + "  @" + row["username"]
            ):
                c1, c2, c3 = st.columns([2, 2, 1])
                c1.markdown(f"**Username:** `{row['username']}`")
                c1.markdown(f"**Email:** {row.get('email', '-') or '-'}")
                c1.markdown(f"**Dibuat:** {str(row.get('created_at', ''))[:10]}")
                c2.markdown(
                    f"**Role:** <span style='color:{rc}'>{row['role'].upper()}</span>",
                    unsafe_allow_html=True
                )
                c2.markdown(
                    f"**Status:** <span style='color:{ac}'>{'AKTIF' if row['is_active'] else 'NONAKTIF'}</span>",
                    unsafe_allow_html=True
                )
                last = str(row.get("last_login", ""))[:16] if row.get("last_login") else "Belum pernah"
                c2.markdown(f"**Login Terakhir:** {last}")

                if row["username"] != current_user.get("username"):
                    with c3:
                        lbl = "🔒 Nonaktifkan" if row["is_active"] else "✅ Aktifkan"
                        if st.button(lbl, key=f"tog_{row['id']}", use_container_width=True):
                            new_val = 0 if row["is_active"] else 1
                            _exec(conn, "UPDATE users SET is_active=%s WHERE id=%s",
                                  (new_val, row["id"]))
                            st.rerun()
                        if row["username"] != "admin":
                            if st.button("🗑️ Hapus", key=f"del_{row['id']}", use_container_width=True):
                                _exec(conn, "DELETE FROM users WHERE id=%s", (row["id"],))
                                st.rerun()

                st.markdown("---")
                with st.form(f"edit_{row['id']}"):
                    new_name  = st.text_input("Nama Lengkap", value=row.get("full_name","") or "", key=f"nm_{row['id']}")
                    new_email = st.text_input("Email",        value=row.get("email","")     or "", key=f"em_{row['id']}")
                    new_role  = st.selectbox("Role", ["admin","viewer"],
                                             index=0 if row["role"]=="admin" else 1,
                                             key=f"rl_{row['id']}")
                    new_pw    = st.text_input("Password Baru (kosongkan jika tidak direset)",
                                              type="password", key=f"pw_{row['id']}")
                    if st.form_submit_button("💾 Simpan Perubahan", use_container_width=True):
                        if new_pw:
                            _exec(conn,
                                  "UPDATE users SET password_hash=%s,role=%s,full_name=%s,email=%s WHERE id=%s",
                                  (hash_password(new_pw), new_role, new_name, new_email, row["id"]))
                        else:
                            _exec(conn,
                                  "UPDATE users SET role=%s,full_name=%s,email=%s WHERE id=%s",
                                  (new_role, new_name, new_email, row["id"]))
                        st.success("User diupdate!")
                        st.rerun()

    with tab2:
        with st.form("add_user"):
            c1, c2 = st.columns(2)
            uname      = c1.text_input("Username*")
            upw        = c1.text_input("Password*", type="password")
            urole      = c1.selectbox("Role", ["viewer","admin"])
            uname_full = c2.text_input("Nama Lengkap")
            uemail     = c2.text_input("Email")
            if st.form_submit_button("➕ Tambah User", use_container_width=True, type="primary"):
                if uname and upw:
                    try:
                        _exec(conn,
                              "INSERT INTO users (username,password_hash,full_name,role,email,is_active) VALUES(%s,%s,%s,%s,%s,1)",
                              (uname, hash_password(upw), uname_full, urole, uemail))
                        st.success(f"User '{uname}' ditambahkan sebagai {urole}!")
                        st.rerun()
                    except Exception as e:
                        if "unique" in str(e).lower():
                            st.error(f"Username '{uname}' sudah digunakan.")
                        else:
                            st.error(f"Error: {e}")
                else:
                    st.error("Username dan password wajib diisi.")

    conn.close()
