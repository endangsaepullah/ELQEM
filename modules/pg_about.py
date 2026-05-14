import streamlit as st
import base64
import os
from utils.database import get_connection
from utils.styles import section_header
from utils.auth import is_admin

# ── Default profile data ───────────────────────────────────
DEFAULT_PROFILE = {
    "name":        "Endang Saefullah, ST, CLA",
    "title":       "Quality Management System Engineer",
    "institution": "Universitas Pertahanan RI (UNHAN)",
    "program":     "Magister Teknik — S2 Defence Industry",
    "year":        "2023 – 2025",
    "email":       "",
    "linkedin":    "",
    "tagline":     "Quality 4.0 | Engineering Lifecycle | Defence Manufacturing",
}

DEFAULT_ABOUT = {
    "platform_bg": (
        "IQLE Platform (Integrated Engineering Quality Lifecycle Evaluation) dikembangkan "
        "sebagai prototype akademik dalam rangka penelitian tesis Magister Teknik di "
        "Universitas Pertahanan RI. Platform ini merupakan implementasi konsep Quality 4.0 "
        "yang mengintegrasikan standar mutu ISO 9001, IATF 16949, Engineering Lifecycle, "
        "serta analisis PLS-SEM untuk mengevaluasi konsistensi mutu produksi Kendaraan "
        "Multifungsi Nasional PT Pindad (Persero)."
    ),
    "thesis_title": (
        "Pengaruh ISO 9001, IATF 16949, dan Engineering Lifecycle terhadap Konsistensi "
        "Mutu Produksi Kendaraan Multifungsi Nasional PT Pindad (Persero)"
    ),
    "thesis_method": (
        "Penelitian menggunakan pendekatan Mixed Methods Sequential Explanatory — diawali "
        "dengan analisis kuantitatif PLS-SEM untuk menguji hubungan antar variabel, "
        "kemudian dilanjutkan wawancara mendalam untuk memperdalam hasil kuantitatif. "
        "Engineering Lifecycle terbukti sebagai faktor paling dominan (koefisien 0,532, "
        "R-Square 0,729)."
    ),
    "vision": (
        "Mengembangkan sistem evaluasi mutu berbasis digital yang dapat diadopsi pada "
        "industri pertahanan nasional, mendukung kemandirian industri strategis, dan "
        "berkontribusi pada peningkatan standar mutu produksi kendaraan taktis Indonesia "
        "menuju Quality 4.0."
    ),
}


# ── Helper: load/save profile text from DB ─────────────────
def get_profile_value(key, default=""):
    try:
        conn = get_connection()
        row = conn.execute(
            "SELECT value FROM about_platform WHERE key = ?", (key,)
        ).fetchone()
        conn.close()
        return row['value'] if row and row['value'] else default
    except Exception:
        return default


def set_profile_value(key, value):
    conn = get_connection()
    conn.execute("""
        INSERT INTO about_platform (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=datetime('now')
    """, (key, value))
    conn.commit()
    conn.close()


# ── Helper: photo from DB ──────────────────────────────────
def get_photo_b64():
    try:
        conn = get_connection()
        row = conn.execute(
            "SELECT photo_data, mime_type FROM about_photo ORDER BY id DESC LIMIT 1"
        ).fetchone()
        conn.close()
        if row and row['photo_data']:
            b64 = base64.b64encode(row['photo_data']).decode()
            return f"data:{row['mime_type']};base64,{b64}"
    except Exception:
        pass
    return None


def save_photo(file_bytes, mime_type, filename):
    conn = get_connection()
    conn.execute("DELETE FROM about_photo")          # keep only one photo
    conn.execute(
        "INSERT INTO about_photo (filename, photo_data, mime_type) VALUES (?, ?, ?)",
        (filename, file_bytes, mime_type)
    )
    conn.commit()
    conn.close()


# ── Default avatar SVG ─────────────────────────────────────
def default_avatar_svg():
    return """
    <svg width="160" height="160" viewBox="0 0 160 160"
         xmlns="http://www.w3.org/2000/svg">
      <circle cx="80" cy="80" r="80" fill="#0d1321"/>
      <circle cx="80" cy="62" r="30" fill="#1e3a5f"/>
      <ellipse cx="80" cy="145" rx="50" ry="35" fill="#1e3a5f"/>
      <circle cx="80" cy="80" r="78" fill="none" stroke="#00d4ff" stroke-width="2"
              stroke-dasharray="6 3" opacity="0.5"/>
    </svg>
    """


# ── Main show() ────────────────────────────────────────────
def show():
    section_header("About Platform", "Profil Peneliti & Latar Belakang IQLE Platform", "👤")

    # Load dynamic values (DB overrides defaults if set)
    name      = get_profile_value("name",      DEFAULT_PROFILE["name"])
    title_pos = get_profile_value("title",     DEFAULT_PROFILE["title"])
    tagline   = get_profile_value("tagline",   DEFAULT_PROFILE["tagline"])
    email     = get_profile_value("email",     DEFAULT_PROFILE["email"])
    linkedin  = get_profile_value("linkedin",  DEFAULT_PROFILE["linkedin"])
    plat_bg   = get_profile_value("platform_bg",  DEFAULT_ABOUT["platform_bg"])
    thesis_t  = get_profile_value("thesis_title", DEFAULT_ABOUT["thesis_title"])
    thesis_m  = get_profile_value("thesis_method",DEFAULT_ABOUT["thesis_method"])
    vision    = get_profile_value("vision",    DEFAULT_ABOUT["vision"])

    photo_src = get_photo_b64()

    # ── SECTION 1: Hero — foto + nama ─────────────────────
    col_photo, col_info = st.columns([1, 2.5])

    with col_photo:
        if photo_src:
            st.markdown(f"""
            <div style="text-align:center;">
                <img src="{photo_src}"
                     style="width:160px; height:160px; object-fit:cover;
                            border-radius:50%; border:3px solid #00d4ff;
                            box-shadow:0 0 24px rgba(0,212,255,0.3);">
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="text-align:center;">
                {default_avatar_svg()}
                <div style="font-size:0.7rem; color:#3d5470; margin-top:0.4rem;
                            letter-spacing:1px;">No Photo</div>
            </div>
            """, unsafe_allow_html=True)

        # Upload foto — admin only
        if is_admin():
            st.markdown("<br>", unsafe_allow_html=True)
            uploaded = st.file_uploader(
                "Upload Foto Profil",
                type=["jpg", "jpeg", "png"],
                help="Format JPG/PNG, maks 2MB",
                key="photo_uploader"
            )
            if uploaded:
                if uploaded.size > 2 * 1024 * 1024:
                    st.error("Ukuran file melebihi 2MB.")
                else:
                    mime = "image/png" if uploaded.name.endswith(".png") else "image/jpeg"
                    save_photo(uploaded.read(), mime, uploaded.name)
                    st.success("Foto berhasil disimpan!")
                    st.rerun()

    with col_info:
        st.markdown(f"""
        <div style="padding:1.5rem 1.75rem;
                    background:linear-gradient(135deg, #0d1321, #111827);
                    border:1px solid rgba(0,212,255,0.2);
                    border-left:4px solid #00d4ff;
                    border-radius:12px;">

            <div style="font-family:'Rajdhani',sans-serif; font-size:1.9rem;
                        font-weight:700; color:#e8edf5; letter-spacing:1px;
                        line-height:1.1; margin-bottom:0.4rem;">
                {name}
            </div>

            <div style="font-size:0.85rem; color:#00d4ff; margin-bottom:0.9rem;
                        font-weight:500;">{title_pos}</div>

            <div style="display:flex; flex-wrap:wrap; gap:0.4rem; margin-bottom:1rem;">
                {"".join(f'<span style="background:rgba(0,212,255,0.1); border:1px solid rgba(0,212,255,0.3); border-radius:4px; padding:2px 10px; font-size:0.72rem; color:#00d4ff; font-family:Rajdhani; font-weight:700; letter-spacing:1px;">{t}</span>' for t in tagline.split(" | "))}
            </div>

            <div style="border-top:1px solid rgba(0,212,255,0.1); padding-top:0.9rem;">
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.5rem;">

                    <div>
                        <div style="font-size:0.65rem; color:#4a6fa5; letter-spacing:1px;
                                    text-transform:uppercase; margin-bottom:0.2rem;">
                            Program Studi
                        </div>
                        <div style="font-size:0.85rem; color:#c5d5e8;">
                            {DEFAULT_PROFILE['program']}
                        </div>
                    </div>

                    <div>
                        <div style="font-size:0.65rem; color:#4a6fa5; letter-spacing:1px;
                                    text-transform:uppercase; margin-bottom:0.2rem;">
                            Institusi
                        </div>
                        <div style="font-size:0.85rem; color:#c5d5e8;">
                            {DEFAULT_PROFILE['institution']}
                        </div>
                    </div>

                    <div>
                        <div style="font-size:0.65rem; color:#4a6fa5; letter-spacing:1px;
                                    text-transform:uppercase; margin-bottom:0.2rem;">
                            S1 — Industrial Engineering
                        </div>
                        <div style="font-size:0.85rem; color:#c5d5e8;">
                            Universitas Mercu Buana &nbsp;
                            <span style="color:#00ff88; font-size:0.78rem;">IPK 3.69 (2020)</span>
                        </div>
                    </div>

                    <div>
                        <div style="font-size:0.65rem; color:#4a6fa5; letter-spacing:1px;
                                    text-transform:uppercase; margin-bottom:0.2rem;">
                            Pengalaman Kerja
                        </div>
                        <div style="font-size:0.85rem; color:#c5d5e8;">
                            PT Wijaya Karya Beton
                            <span style="color:#ffd700; font-size:0.78rem;">— Jan 2017 s/d Sekarang</span>
                        </div>
                    </div>

                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── SECTION 2: Latar Belakang Platform ────────────────
    st.markdown("#### 🏭 Latar Belakang IQLE Platform")
    st.markdown(f"""
    <div style="padding:1rem 1.25rem; background:#111827;
                border:1px solid rgba(0,212,255,0.15); border-radius:10px;
                font-size:0.87rem; color:#c5d5e8; line-height:1.75;
                margin-bottom:1rem;">
        {plat_bg}
    </div>
    """, unsafe_allow_html=True)

    # ── SECTION 3: Keterkaitan Tesis ──────────────────────
    st.markdown("#### 🎓 Keterkaitan dengan Tesis")
    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.markdown(f"""
        <div style="padding:1rem 1.25rem; background:#111827;
                    border:1px solid rgba(255,215,0,0.2);
                    border-left:3px solid #ffd700; border-radius:8px; height:100%;">
            <div style="font-size:0.65rem; color:#ffd700; letter-spacing:2px;
                        text-transform:uppercase; margin-bottom:0.5rem;">
                Judul Tesis
            </div>
            <div style="font-size:0.85rem; color:#e8edf5; line-height:1.65;
                        font-style:italic;">
                "{thesis_t}"
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_t2:
        st.markdown(f"""
        <div style="padding:1rem 1.25rem; background:#111827;
                    border:1px solid rgba(0,255,136,0.2);
                    border-left:3px solid #00ff88; border-radius:8px; height:100%;">
            <div style="font-size:0.65rem; color:#00ff88; letter-spacing:2px;
                        text-transform:uppercase; margin-bottom:0.5rem;">
                Metode & Temuan Utama
            </div>
            <div style="font-size:0.85rem; color:#c5d5e8; line-height:1.65;">
                {thesis_m}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # PLS-SEM result bar mini
    st.markdown("<br>", unsafe_allow_html=True)
    results = [
        ("ISO 9001 (X1)",              0.318, "#00d4ff"),
        ("IATF 16949 (X2)",            0.217, "#0066ff"),
        ("Engineering Lifecycle (X3)", 0.532, "#00ff88"),
    ]
    rc1, rc2, rc3 = st.columns(3)
    for col, (label, coef, color) in zip([rc1, rc2, rc3], results):
        pct = int(coef * 100 / 0.6 * 100)
        col.markdown(f"""
        <div style="padding:0.85rem 1rem; background:#111827;
                    border:1px solid {color}33; border-radius:8px; text-align:center;">
            <div style="font-size:0.7rem; color:#7a9bb5; margin-bottom:0.4rem;">{label}</div>
            <div style="font-family:'Rajdhani',sans-serif; font-size:1.8rem;
                        font-weight:700; color:{color};">{coef}</div>
            <div style="background:#0d1321; border-radius:4px; height:5px;
                        margin-top:0.5rem; overflow:hidden;">
                <div style="background:{color}; height:100%; width:{pct}%;
                            border-radius:4px;"></div>
            </div>
            <div style="font-size:0.65rem; color:{color}; margin-top:0.3rem;">koefisien jalur</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── SECTION 4: Kompetensi ─────────────────────────────
    st.markdown("#### 🛠️ Kompetensi Pendukung")

    comp_col1, comp_col2 = st.columns(2)

    with comp_col1:
        st.markdown("""
        <div style="padding:1rem 1.25rem; background:#111827;
                    border:1px solid rgba(0,212,255,0.15); border-radius:10px;
                    margin-bottom:0.75rem;">
            <div style="font-size:0.7rem; color:#00d4ff; letter-spacing:2px;
                        text-transform:uppercase; margin-bottom:0.75rem; font-weight:700;">
                Keahlian Utama
            </div>
        """, unsafe_allow_html=True)

        skills = [
            ("Pengembangan Sistem Manajemen Mutu",  "#00d4ff"),
            ("Penyusunan Prosedur & Dokumen Kerja", "#00d4ff"),
            ("Audit Internal & Eksternal",          "#0066ff"),
            ("Process Digitalization",              "#00ff88"),
            ("Industrial Management",               "#00ff88"),
            ("System Design & Engineering",         "#ffd700"),
        ]
        for skill, color in skills:
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:0.6rem;
                        padding:0.35rem 0; border-bottom:1px solid rgba(255,255,255,0.04);">
                <div style="width:6px; height:6px; border-radius:50%;
                            background:{color}; flex-shrink:0;"></div>
                <span style="font-size:0.83rem; color:#c5d5e8;">{skill}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with comp_col2:
        st.markdown("""
        <div style="padding:1rem 1.25rem; background:#111827;
                    border:1px solid rgba(0,255,136,0.15); border-radius:10px;
                    margin-bottom:0.75rem;">
            <div style="font-size:0.7rem; color:#00ff88; letter-spacing:2px;
                        text-transform:uppercase; margin-bottom:0.75rem; font-weight:700;">
                Sertifikasi & Pelatihan
            </div>
        """, unsafe_allow_html=True)

        certs = [
            ("Certified Lead Auditor ISO 9001:2015 (IRCA)", "#00ff88", "CLA"),
            ("K3 Expert — PP 50/2012",                       "#ffd700", "K3"),
            ("ISO 37001 — Anti-Bribery Management",          "#00d4ff", "ISO"),
            ("ISO 27001 — Information Security",             "#00d4ff", "ISO"),
            ("ISO 45001 — Occupational Health & Safety",     "#0066ff", "ISO"),
            ("ISO 14001 — Environmental Management",         "#0066ff", "ISO"),
            ("ISO 17025 — Testing & Calibration Lab",        "#a78bfa", "ISO"),
        ]
        for cert, color, badge in certs:
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:0.6rem;
                        padding:0.35rem 0; border-bottom:1px solid rgba(255,255,255,0.04);">
                <span style="background:rgba(0,0,0,0.3); border:1px solid {color}55;
                             border-radius:3px; padding:1px 5px; font-size:0.6rem;
                             color:{color}; font-family:Rajdhani; font-weight:700;
                             flex-shrink:0; letter-spacing:0.5px;">{badge}</span>
                <span style="font-size:0.82rem; color:#c5d5e8;">{cert}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ── SECTION 5: Visi Pengembangan ──────────────────────
    st.markdown("#### 🚀 Visi Pengembangan")
    st.markdown(f"""
    <div style="padding:1.1rem 1.4rem; background:linear-gradient(135deg,
                rgba(0,212,255,0.05), rgba(0,255,136,0.05));
                border:1px solid rgba(0,255,136,0.2); border-radius:10px;
                font-size:0.87rem; color:#c5d5e8; line-height:1.75;
                margin-bottom:1rem;">
        {vision}
    </div>
    """, unsafe_allow_html=True)

    vision_items = [
        ("Quality 4.0",                "Digitalisasi sistem evaluasi mutu berbasis data analytics dan dashboard interaktif.",    "#00d4ff"),
        ("Engineering Lifecycle",      "Penguatan pengendalian siklus rekayasa pada industri kendaraan taktis nasional.",       "#00ff88"),
        ("Defence Manufacturing",      "Peningkatan standar mutu produksi industri pertahanan menuju kemandirian strategis.",   "#ffd700"),
    ]

    vc1, vc2, vc3 = st.columns(3)
    for col, (title, desc, color) in zip([vc1, vc2, vc3], vision_items):
        h = color.lstrip('#')
        rv, gv, bv = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        col.markdown(f"""
        <div style="padding:1rem; background:#111827;
                    border:1px solid rgba({rv},{gv},{bv},0.25);
                    border-top:3px solid {color}; border-radius:8px;
                    text-align:center; height:100%;">
            <div style="font-family:'Rajdhani',sans-serif; font-size:1rem;
                        font-weight:700; color:{color}; margin-bottom:0.5rem;
                        letter-spacing:1px;">{title}</div>
            <div style="font-size:0.8rem; color:#7a9bb5; line-height:1.55;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── SECTION 6: Edit profil (Admin only) ───────────────
    if is_admin():
        with st.expander("✏️  Edit Teks Profil [Admin Only]", expanded=False):
            st.markdown("""
            <div style="padding:0.5rem 0.75rem; background:rgba(255,215,0,0.07);
                        border:1px solid rgba(255,215,0,0.2); border-radius:6px;
                        font-size:0.78rem; color:#ffd700; margin-bottom:1rem;">
                Perubahan disimpan ke database dan langsung aktif.
                Kosongkan field untuk kembali ke nilai default.
            </div>
            """, unsafe_allow_html=True)

            with st.form("edit_about_form"):
                e_name  = st.text_input("Nama Lengkap",     value=name)
                e_title = st.text_input("Jabatan / Posisi", value=title_pos)
                e_tag   = st.text_input(
                    "Tagline (pisahkan dengan ' | ')", value=tagline
                )
                e_bg    = st.text_area("Latar Belakang Platform", value=plat_bg,     height=120)
                e_tit   = st.text_area("Judul Tesis",              value=thesis_t,   height=80)
                e_mth   = st.text_area("Metode & Temuan",          value=thesis_m,   height=100)
                e_vis   = st.text_area("Visi Pengembangan",        value=vision,     height=100)

                if st.form_submit_button("💾 Simpan Profil", use_container_width=True, type="primary"):
                    mapping = {
                        "name": e_name, "title": e_title, "tagline": e_tag,
                        "platform_bg": e_bg, "thesis_title": e_tit,
                        "thesis_method": e_mth, "vision": e_vis,
                    }
                    for k, v in mapping.items():
                        if v.strip():
                            set_profile_value(k, v.strip())
                    st.success("✅ Profil berhasil disimpan!")
                    st.rerun()

    # ── Footer ─────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="padding:0.75rem 1rem; background:rgba(0,0,0,0.3);
                border:1px solid rgba(255,255,255,0.06); border-radius:8px;
                text-align:center; font-size:0.75rem; color:#3d5470;">
        IQLE Platform &nbsp;|&nbsp; Prototype Akademik Magister Teknik &nbsp;|&nbsp;
        PT Pindad (Persero) &nbsp;|&nbsp; Universitas Pertahanan RI
    </div>
    """, unsafe_allow_html=True)
