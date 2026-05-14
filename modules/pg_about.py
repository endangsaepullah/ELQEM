import streamlit as st
import base64
from utils.database import get_connection
from utils.styles import section_header
from utils.auth import is_admin

# ── Static profile data ────────────────────────────────────
PROFILE = {
    "name":        "Endang Saefullah, ST, CLA",
    "title":       "Quality Management System Engineer",
    "institution": "Universitas Pertahanan RI (UNHAN)",
    "program":     "Magister Teknik — S2 Defence Industry",
    "s1":          "Industrial Engineering, Universitas Mercu Buana",
    "ipk":         "IPK 3.69 (2020)",
    "company":     "PT Wijaya Karya Beton",
    "period":      "Jan 2017 — Sekarang",
    "tags":        ["Quality 4.0", "Engineering Lifecycle", "Defence Manufacturing"],
}

DEFAULT = {
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
        "Engineering Lifecycle terbukti sebagai faktor paling dominan "
        "(koefisien 0,532, R-Square 0,729)."
    ),
    "vision": (
        "Mengembangkan sistem evaluasi mutu berbasis digital yang dapat diadopsi pada "
        "industri pertahanan nasional, mendukung kemandirian industri strategis, dan "
        "berkontribusi pada peningkatan standar mutu produksi kendaraan taktis Indonesia "
        "menuju Quality 4.0."
    ),
}

# ── DB helpers ─────────────────────────────────────────────

def db_get(key, default=""):
    try:
        conn = get_connection()
        row = conn.execute(
            "SELECT value FROM about_platform WHERE key=?", (key,)
        ).fetchone()
        conn.close()
        return row["value"] if (row and row["value"]) else default
    except Exception:
        return default


def db_set(key, value):
    conn = get_connection()
    conn.execute(
        "INSERT INTO about_platform (key,value) VALUES(?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=datetime('now')",
        (key, value)
    )
    conn.commit()
    conn.close()


def get_photo_b64():
    try:
        conn = get_connection()
        row = conn.execute(
            "SELECT photo_data, mime_type FROM about_photo ORDER BY id DESC LIMIT 1"
        ).fetchone()
        conn.close()
        if row and row["photo_data"]:
            b64 = base64.b64encode(row["photo_data"]).decode()
            return "data:" + row["mime_type"] + ";base64," + b64
    except Exception:
        pass
    return None


def save_photo(file_bytes, mime_type, filename):
    conn = get_connection()
    conn.execute("DELETE FROM about_photo")
    conn.execute(
        "INSERT INTO about_photo (filename,photo_data,mime_type) VALUES(?,?,?)",
        (filename, file_bytes, mime_type)
    )
    conn.commit()
    conn.close()

# ── Helpers: small HTML blocks (no nested f-strings) ───────

def _label(text):
    return (
        '<p style="font-size:0.65rem;color:#4a6fa5;letter-spacing:1px;'
        'text-transform:uppercase;margin:0 0 3px 0;">' + text + "</p>"
    )


def _value(text, color="#c5d5e8"):
    return (
        '<p style="font-size:0.85rem;color:' + color + ';margin:0 0 0.75rem 0;">'
        + text + "</p>"
    )


def _badge(text, color="#00d4ff"):
    style = (
        "display:inline-block;margin:0 4px 4px 0;"
        "background:rgba(0,212,255,0.1);"
        "border:1px solid rgba(0,212,255,0.35);"
        "border-radius:4px;padding:2px 10px;"
        "font-size:0.72rem;color:" + color + ";"
        "font-family:Rajdhani,sans-serif;"
        "font-weight:700;letter-spacing:1px;"
    )
    return "<span style='" + style + "'>" + text + "</span>"


def _card(content, border_color="#00d4ff", extra_style=""):
    style = (
        "padding:0.85rem 1.1rem;"
        "background:#111827;"
        "border:1px solid rgba(0,212,255,0.15);"
        "border-left:3px solid " + border_color + ";"
        "border-radius:8px;margin-bottom:0.5rem;" + extra_style
    )
    return "<div style='" + style + "'>" + content + "</div>"


# ── Main ───────────────────────────────────────────────────

def show():
    section_header(
        "About Platform",
        "Profil Peneliti & Latar Belakang IQLE Platform",
        "👤"
    )

    # Load from DB
    plat_bg  = db_get("platform_bg",   DEFAULT["platform_bg"])
    thesis_t = db_get("thesis_title",  DEFAULT["thesis_title"])
    thesis_m = db_get("thesis_method", DEFAULT["thesis_method"])
    vision   = db_get("vision",        DEFAULT["vision"])

    photo_src = get_photo_b64()

    # ══ SECTION 1 — Hero ══════════════════════════════════
    col_photo, col_info = st.columns([1, 2.5])

    # — Foto —
    with col_photo:
        if photo_src:
            img_style = (
                "width:160px;height:160px;object-fit:cover;"
                "border-radius:50%;border:3px solid #00d4ff;"
                "box-shadow:0 0 24px rgba(0,212,255,0.3);"
                "display:block;margin:0 auto;"
            )
            st.markdown(
                "<img src='" + photo_src + "' style='" + img_style + "'>",
                unsafe_allow_html=True
            )
        else:
            avatar = (
                '<div style="text-align:center;">'
                '<svg width="160" height="160" viewBox="0 0 160 160" '
                'xmlns="http://www.w3.org/2000/svg">'
                '<circle cx="80" cy="80" r="80" fill="#0d1321"/>'
                '<circle cx="80" cy="62" r="30" fill="#1e3a5f"/>'
                '<ellipse cx="80" cy="145" rx="50" ry="35" fill="#1e3a5f"/>'
                '<circle cx="80" cy="80" r="78" fill="none" stroke="#00d4ff" '
                'stroke-width="2" stroke-dasharray="6 3" opacity="0.5"/>'
                '</svg>'
                '<div style="font-size:0.7rem;color:#3d5470;margin-top:4px;">No Photo</div>'
                '</div>'
            )
            st.markdown(avatar, unsafe_allow_html=True)

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
                    st.success("Foto tersimpan!")
                    st.rerun()

    # — Info profil —
    with col_info:
        # Nama
        nama_html = (
            '<div style="padding:1rem 1.25rem;'
            'background:linear-gradient(135deg,#0d1321,#111827);'
            'border:1px solid rgba(0,212,255,0.2);'
            'border-left:4px solid #00d4ff;border-radius:12px;margin-bottom:0.6rem;">'
            '<div style="font-family:Rajdhani,sans-serif;font-size:1.85rem;'
            'font-weight:700;color:#e8edf5;letter-spacing:1px;line-height:1.1;'
            'margin-bottom:0.3rem;">' + PROFILE["name"] + "</div>"
            '<div style="font-size:0.85rem;color:#00d4ff;font-weight:500;'
            'margin-bottom:0;">' + PROFILE["title"] + "</div>"
            "</div>"
        )
        st.markdown(nama_html, unsafe_allow_html=True)

        # Tags
        tags_html = "".join(_badge(t) for t in PROFILE["tags"])
        st.markdown(
            '<div style="margin-bottom:0.75rem;">' + tags_html + "</div>",
            unsafe_allow_html=True
        )

        # Grid info
        ga, gb = st.columns(2)
        with ga:
            st.markdown(
                _label("Program Studi") + _value(PROFILE["program"]),
                unsafe_allow_html=True
            )
            st.markdown(
                _label("S1 Industrial Engineering")
                + _value(PROFILE["s1"]
                         + ' <span style="color:#00ff88;font-size:0.78rem;">'
                         + PROFILE["ipk"] + "</span>"),
                unsafe_allow_html=True
            )
        with gb:
            st.markdown(
                _label("Institusi S2") + _value(PROFILE["institution"]),
                unsafe_allow_html=True
            )
            st.markdown(
                _label("Pengalaman Kerja")
                + _value(PROFILE["company"]
                         + ' <span style="color:#ffd700;font-size:0.78rem;">'
                         + PROFILE["period"] + "</span>"),
                unsafe_allow_html=True
            )

    st.markdown("---")

    # ══ SECTION 2 — Latar Belakang ════════════════════════
    st.markdown("#### Latar Belakang IQLE Platform")
    bg_html = (
        '<div style="padding:1rem 1.25rem;background:#111827;'
        'border:1px solid rgba(0,212,255,0.15);border-radius:10px;'
        'font-size:0.87rem;color:#c5d5e8;line-height:1.75;">'
        + plat_bg + "</div>"
    )
    st.markdown(bg_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ══ SECTION 3 — Keterkaitan Tesis ════════════════════
    st.markdown("#### Keterkaitan dengan Tesis")
    t1, t2 = st.columns(2)

    with t1:
        st.markdown(
            _card(
                _label("Judul Tesis")
                + '<p style="font-size:0.85rem;color:#e8edf5;line-height:1.65;'
                'font-style:italic;margin:0;">&ldquo;' + thesis_t + "&rdquo;</p>",
                border_color="#ffd700"
            ),
            unsafe_allow_html=True
        )
    with t2:
        st.markdown(
            _card(
                _label("Metode &amp; Temuan Utama")
                + '<p style="font-size:0.85rem;color:#c5d5e8;line-height:1.65;margin:0;">'
                + thesis_m + "</p>",
                border_color="#00ff88"
            ),
            unsafe_allow_html=True
        )

    # PLS-SEM mini bars
    st.markdown("<br>", unsafe_allow_html=True)
    results = [
        ("ISO 9001 (X1)",              0.318, "#00d4ff"),
        ("IATF 16949 (X2)",            0.217, "#0066ff"),
        ("Engineering Lifecycle (X3)", 0.532, "#00ff88"),
    ]
    rc1, rc2, rc3 = st.columns(3)
    for col, (label, coef, color) in zip([rc1, rc2, rc3], results):
        pct = int(coef / 0.6 * 100)
        bar_html = (
            '<div style="padding:0.85rem 1rem;background:#111827;'
            'border:1px solid ' + color + '33;border-radius:8px;text-align:center;">'
            '<div style="font-size:0.7rem;color:#7a9bb5;margin-bottom:0.4rem;">'
            + label + "</div>"
            '<div style="font-family:Rajdhani,sans-serif;font-size:1.8rem;'
            'font-weight:700;color:' + color + ';">' + str(coef) + "</div>"
            '<div style="background:#0d1321;border-radius:4px;height:5px;'
            'margin-top:0.5rem;overflow:hidden;">'
            '<div style="background:' + color + ';height:100%;width:' + str(pct)
            + '%;border-radius:4px;"></div></div>'
            '<div style="font-size:0.65rem;color:' + color
            + ';margin-top:0.3rem;">koefisien jalur</div>'
            "</div>"
        )
        col.markdown(bar_html, unsafe_allow_html=True)

    st.markdown("---")

    # ══ SECTION 4 — Kompetensi ════════════════════════════
    st.markdown("#### Kompetensi Pendukung")
    sk1, sk2 = st.columns(2)

    with sk1:
        st.markdown(
            '<div style="padding:1rem 1.25rem;background:#111827;'
            'border:1px solid rgba(0,212,255,0.15);border-radius:10px;">',
            unsafe_allow_html=True
        )
        st.markdown(
            _label("Keahlian Utama"),
            unsafe_allow_html=True
        )
        skills = [
            "Pengembangan Sistem Manajemen Mutu",
            "Penyusunan Prosedur & Dokumen Kerja",
            "Audit Internal & Eksternal",
            "Process Digitalization",
            "Industrial Management",
            "System Design & Engineering",
        ]
        for s in skills:
            st.markdown(
                '<div style="display:flex;align-items:center;gap:0.6rem;'
                'padding:0.35rem 0;border-bottom:1px solid rgba(255,255,255,0.04);">'
                '<div style="width:6px;height:6px;border-radius:50%;'
                'background:#00d4ff;flex-shrink:0;"></div>'
                '<span style="font-size:0.83rem;color:#c5d5e8;">' + s + "</span>"
                "</div>",
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with sk2:
        st.markdown(
            '<div style="padding:1rem 1.25rem;background:#111827;'
            'border:1px solid rgba(0,255,136,0.15);border-radius:10px;">',
            unsafe_allow_html=True
        )
        st.markdown(_label("Sertifikasi &amp; Pelatihan"), unsafe_allow_html=True)
        certs = [
            ("Certified Lead Auditor ISO 9001:2015 (IRCA)", "#00ff88", "CLA"),
            ("K3 Expert — PP 50/2012",                      "#ffd700", "K3"),
            ("ISO 37001 — Anti-Bribery Management",         "#00d4ff", "ISO"),
            ("ISO 27001 — Information Security",            "#00d4ff", "ISO"),
            ("ISO 45001 — Occupational Health & Safety",    "#0066ff", "ISO"),
            ("ISO 14001 — Environmental Management",        "#0066ff", "ISO"),
            ("ISO 17025 — Testing & Calibration Lab",       "#a78bfa", "ISO"),
        ]
        for cert, color, badge in certs:
            st.markdown(
                '<div style="display:flex;align-items:center;gap:0.6rem;'
                'padding:0.35rem 0;border-bottom:1px solid rgba(255,255,255,0.04);">'
                '<span style="background:rgba(0,0,0,0.3);border:1px solid '
                + color + '55;border-radius:3px;padding:1px 5px;font-size:0.6rem;'
                'color:' + color + ';font-family:Rajdhani;font-weight:700;'
                'flex-shrink:0;letter-spacing:0.5px;">' + badge + "</span>"
                '<span style="font-size:0.82rem;color:#c5d5e8;">' + cert + "</span>"
                "</div>",
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ══ SECTION 5 — Visi ══════════════════════════════════
    st.markdown("#### Visi Pengembangan")
    st.markdown(
        '<div style="padding:1.1rem 1.4rem;background:linear-gradient(135deg,'
        'rgba(0,212,255,0.05),rgba(0,255,136,0.05));'
        'border:1px solid rgba(0,255,136,0.2);border-radius:10px;'
        'font-size:0.87rem;color:#c5d5e8;line-height:1.75;margin-bottom:1rem;">'
        + vision + "</div>",
        unsafe_allow_html=True
    )

    vc1, vc2, vc3 = st.columns(3)
    vision_cards = [
        ("Quality 4.0",           "Digitalisasi sistem evaluasi mutu berbasis data analytics dan dashboard interaktif.",   "#00d4ff"),
        ("Engineering Lifecycle", "Penguatan pengendalian siklus rekayasa pada industri kendaraan taktis nasional.",       "#00ff88"),
        ("Defence Manufacturing", "Peningkatan standar mutu produksi industri pertahanan menuju kemandirian strategis.",   "#ffd700"),
    ]
    for col, (title, desc, color) in zip([vc1, vc2, vc3], vision_cards):
        card_html = (
            '<div style="padding:1rem;background:#111827;'
            'border:1px solid ' + color + '33;'
            'border-top:3px solid ' + color + ';'
            'border-radius:8px;text-align:center;">'
            '<div style="font-family:Rajdhani,sans-serif;font-size:1rem;'
            'font-weight:700;color:' + color + ';margin-bottom:0.5rem;'
            'letter-spacing:1px;">' + title + "</div>"
            '<div style="font-size:0.8rem;color:#7a9bb5;line-height:1.55;">'
            + desc + "</div>"
            "</div>"
        )
        col.markdown(card_html, unsafe_allow_html=True)

    st.markdown("---")

    # ══ SECTION 6 — Edit Profil (Admin) ══════════════════
    if is_admin():
        with st.expander("Edit Teks Profil [Admin Only]", expanded=False):
            st.info("Perubahan disimpan ke database dan langsung aktif.")
            with st.form("edit_about_form"):
                e_bg  = st.text_area("Latar Belakang Platform", value=plat_bg,  height=120)
                e_tt  = st.text_area("Judul Tesis",              value=thesis_t, height=80)
                e_tm  = st.text_area("Metode & Temuan",          value=thesis_m, height=100)
                e_vis = st.text_area("Visi Pengembangan",        value=vision,   height=100)
                if st.form_submit_button("Simpan", use_container_width=True, type="primary"):
                    for k, v in [
                        ("platform_bg",   e_bg),
                        ("thesis_title",  e_tt),
                        ("thesis_method", e_tm),
                        ("vision",        e_vis),
                    ]:
                        if v.strip():
                            db_set(k, v.strip())
                    st.success("Profil berhasil disimpan!")
                    st.rerun()

    # ══ Footer ════════════════════════════════════════════
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="padding:0.75rem 1rem;background:rgba(0,0,0,0.3);'
        'border:1px solid rgba(255,255,255,0.06);border-radius:8px;'
        'text-align:center;font-size:0.75rem;color:#3d5470;">'
        "IQLE Platform &nbsp;|&nbsp; Prototype Akademik Magister Teknik &nbsp;|&nbsp; "
        "PT Pindad (Persero) &nbsp;|&nbsp; Universitas Pertahanan RI"
        "</div>",
        unsafe_allow_html=True
    )
