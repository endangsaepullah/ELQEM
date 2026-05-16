import streamlit as st
from utils.database import fetchall, fetchone, execute, get_category, get_lifecycle_maturity
from utils.styles import section_header
from utils.auth import require_admin, is_admin, hash_password


def db_write(sql, params=()):
    """Helper: buka koneksi baru, execute, commit, tutup."""
    execute(sql, params)


def show():
    require_admin()
    section_header("Manajemen User", "Role-Based Access Control", "👥")
    tab1, tab2 = st.tabs(["👤 Daftar User", "➕ Tambah User"])

    current_user = st.session_state.get("user", {})

    with tab1:
        # Baca data dengan koneksi sendiri
        rows = fetchall(
            "SELECT id,username,full_name,role,email,is_active,created_at,last_login "
            "FROM users ORDER BY id"
        )

        for row in rows:
            rc = "#00d4ff" if row["role"] == "admin" else "#ffd700"
            ac = "#00ff88" if row["is_active"] else "#ff3366"
            label = ("🔑 " if row["role"] == "admin" else "👁 ") \
                    + (row["full_name"] or row["username"]) + "  @" + row["username"]

            with st.expander(label):
                c1, c2, c3 = st.columns([2, 2, 1])
                c1.markdown(f"**Username:** `{row['username']}`")
                c1.markdown(f"**Email:** {row['email'] or '-'}")
                c1.markdown(f"**Dibuat:** {str(row['created_at'] or '')[:10]}")
                c2.markdown(
                    f"**Role:** <span style='color:{rc}'>{row['role'].upper()}</span>",
                    unsafe_allow_html=True
                )
                c2.markdown(
                    f"**Status:** <span style='color:{ac}'>"
                    f"{'AKTIF' if row['is_active'] else 'NONAKTIF'}</span>",
                    unsafe_allow_html=True
                )
                last = str(row["last_login"] or "")[:16] or "Belum pernah"
                c2.markdown(f"**Login Terakhir:** {last}")

                if row["username"] != current_user.get("username"):
                    with c3:
                        lbl = "🔒 Nonaktifkan" if row["is_active"] else "✅ Aktifkan"
                        if st.button(lbl, key=f"tog_{row['id']}", use_container_width=True):
                            db_write(
                                "UPDATE users SET is_active=? WHERE id=?",
                                (0 if row["is_active"] else 1, row["id"])
                            )
                            st.rerun()

                        if row["username"] != "admin":
                            if st.button("🗑️ Hapus", key=f"del_{row['id']}",
                                         use_container_width=True):
                                db_write("DELETE FROM users WHERE id=?", (row["id"],))
                                st.rerun()

                st.markdown("---")
                with st.form(f"edit_{row['id']}"):
                    new_name  = st.text_input("Nama Lengkap",
                                              value=row["full_name"] or "",
                                              key=f"nm_{row['id']}")
                    new_email = st.text_input("Email",
                                              value=row["email"] or "",
                                              key=f"em_{row['id']}")
                    new_role  = st.selectbox("Role", ["admin", "viewer"],
                                             index=0 if row["role"] == "admin" else 1,
                                             key=f"rl_{row['id']}")
                    new_pw    = st.text_input(
                        "Password Baru (kosongkan jika tidak direset)",
                        type="password", key=f"pw_{row['id']}"
                    )
                    if st.form_submit_button("💾 Simpan Perubahan",
                                             use_container_width=True):
                        if new_pw:
                            db_write(
                                "UPDATE users SET password_hash=?,role=?,full_name=?,email=? WHERE id=?",
                                (hash_password(new_pw), new_role, new_name, new_email, row["id"])
                            )
                        else:
                            db_write(
                                "UPDATE users SET role=?,full_name=?,email=? WHERE id=?",
                                (new_role, new_name, new_email, row["id"])
                            )
                        st.success("✅ User diupdate!")
                        st.rerun()

    with tab2:
        with st.form("add_user"):
            col1, col2 = st.columns(2)
            uname  = col1.text_input("Username*")
            upw    = col1.text_input("Password*", type="password")
            urole  = col1.selectbox("Role", ["viewer", "admin"])
            ufull  = col2.text_input("Nama Lengkap")
            uemail = col2.text_input("Email")

            if st.form_submit_button("➕ Tambah User",
                                     use_container_width=True, type="primary"):
                if uname and upw:
                    try:
                        db_write(
                            "INSERT INTO users "
                            "(username,password_hash,full_name,role,email,is_active) "
                            "VALUES (?,?,?,?,?,1)",
                            (uname, hash_password(upw), ufull, urole, uemail)
                        )
                        st.success(f"✅ User '{uname}' berhasil ditambahkan sebagai {urole}!")
                        st.rerun()
                    except Exception as e:
                        if "UNIQUE" in str(e):
                            st.error(f"❌ Username '{uname}' sudah digunakan.")
                        else:
                            st.error(f"❌ Error: {e}")
                else:
                    st.error("❌ Username dan password wajib diisi.")
