import streamlit as st
from utils.styles import section_header


def show():
    section_header(
        "Teori & Referensi Pendukung",
        "Landasan Akademik IQLE Platform — Magister Teknik",
        "📚"
    )

    # ── Pendahuluan ────────────────────────────────────────
    st.markdown("""
    <div style="padding:1.1rem 1.4rem; background:rgba(0,212,255,0.06);
                border:1px solid rgba(0,212,255,0.25); border-radius:10px;
                margin-bottom:1.5rem; line-height:1.7; font-size:0.88rem; color:#c5d5e8;">
        <b style="color:#00d4ff; font-family:'Rajdhani',sans-serif;
                  font-size:1rem; letter-spacing:1px;">TENTANG PLATFORM INI</b><br><br>
        <b>IQLE Platform</b> (Integrated Engineering Quality Lifecycle Evaluation) dikembangkan
        sebagai <b>prototype akademik berbasis Quality 4.0</b> untuk mendukung penelitian tesis
        Magister Teknik dengan fokus evaluasi mutu produksi Kendaraan Multifungsi Nasional
        PT Pindad (Persero).<br><br>
        Platform ini mengintegrasikan empat dimensi evaluasi mutu:
        <b>ISO 9001</b> (X1), <b>IATF 16949</b> (X2), <b>Engineering Lifecycle</b> (X3),
        dan <b>Konsistensi Mutu Produksi</b> (Y) — yang hubungan pengaruhnya diuji melalui
        analisis <b>PLS-SEM</b>, kemudian diperdalam secara kualitatif melalui
        <b>wawancara (Mixed Methods Sequential Explanatory)</b>.
    </div>
    """, unsafe_allow_html=True)

    # ── Teori Pendukung ────────────────────────────────────
    st.markdown("### 📖 Teori Pendukung Utama")
    st.markdown("<br>", unsafe_allow_html=True)

    theories = [
        {
            "id": "A",
            "title": "Quality 4.0",
            "color": "#00d4ff",
            "icon": "🔷",
            "var": "X — Kerangka Utama Platform",
            "body": """
Quality 4.0 merupakan evolusi manajemen mutu yang mengintegrasikan prinsip-prinsip
Total Quality Management (TQM) dengan teknologi Industri 4.0 — mencakup digitalisasi,
Internet of Things (IoT), data analytics, kecerdasan buatan, dan sistem monitoring berbasis
dashboard real-time.

Konsep ini menekankan bahwa kualitas tidak hanya dikelola secara manual melalui inspeksi,
tetapi harus dimonitor secara <i>continuous</i>, berbasis data, dan terintegrasi di seluruh
rantai nilai produksi.
            """,
            "relevance": "KPI mutu real-time, defect analytics, Integrated Quality Lifecycle Score (IQLS), rekomendasi otomatis, dan digital monitoring seluruh modul dashboard."
        },
        {
            "id": "B",
            "title": "ISO 9001:2015 — Quality Management System",
            "color": "#00d4ff",
            "icon": "📊",
            "var": "X1 — Variabel Independen",
            "body": """
ISO 9001:2015 adalah standar internasional sistem manajemen mutu (SMM) berbasis
<i>risk-based thinking</i> dan pendekatan proses. Standar ini mensyaratkan organisasi
untuk mendokumentasikan proses, melakukan audit internal, menerapkan tindakan korektif
terhadap ketidaksesuaian, serta mendorong perbaikan berkelanjutan (<i>continuous improvement</i>).

Lima indikator utama yang diadopsi dalam penelitian ini:
Dokumentasi Proses, Pengendalian Proses, Audit Internal, Tindakan Korektif, dan
Continuous Improvement.
            """,
            "relevance": "Modul ISO 9001, evaluasi skor X1, radar chart indikator, dan trend skor evaluasi."
        },
        {
            "id": "C",
            "title": "IATF 16949:2016 — Automotive Quality Management",
            "color": "#0066ff",
            "icon": "🏭",
            "var": "X2 — Variabel Independen",
            "body": """
IATF 16949:2016 adalah standar sistem manajemen mutu khusus industri otomotif yang
dikembangkan oleh International Automotive Task Force. Standar ini memperluas persyaratan
ISO 9001 dengan penekanan pada <i>defect prevention</i>, <i>risk-based thinking</i>,
pengendalian kualitas pemasok (<i>supplier quality</i>), dan reduksi variasi serta
pemborosan di seluruh rantai pasokan.

Empat indikator utama: Risk-Based Thinking, Defect Prevention,
Supplier Quality, dan Continuous Improvement.
            """,
            "relevance": "Modul IATF 16949, evaluasi supplier quality, defect prevention, monitoring proses produksi kendaraan multifungsi, dan evaluasi skor X2."
        },
        {
            "id": "D",
            "title": "Engineering Lifecycle / Systems Engineering Lifecycle",
            "color": "#00ff88",
            "icon": "⚙️",
            "var": "X3 — Variabel Dominan (PLS-SEM)",
            "body": """
Engineering Lifecycle atau Systems Engineering Lifecycle (INCOSE, 2023) mencakup
keseluruhan siklus rekayasa sistem mulai dari <i>concept</i>, <i>design</i>,
<i>development</i>, <i>manufacturing</i>, <i>verification</i>, <i>validation</i>,
<i>operation</i>, hingga <i>disposal</i>.

Aspek kritis yang ditekankan dalam konteks kendaraan multifungsi nasional adalah:
Design Control, Change Control (ECO — Engineering Change Order), Verification &
Validation, Integration Process, Traceability, dan Communication of Design Change.

Pengelolaan lifecycle rekayasa yang lemah — khususnya change control yang tidak
terstruktur — terbukti menjadi sumber utama defect dan inkonsistensi mutu pada
tahap produksi.
            """,
            "relevance": "Modul Engineering Lifecycle, maturity level assessment, area kritis, trend lifecycle score, dan sebagai faktor paling dominan dalam model PLS-SEM (koefisien 0,532)."
        },
        {
            "id": "E",
            "title": "PLS-SEM — Partial Least Squares Structural Equation Modeling",
            "color": "#ffd700",
            "icon": "📐",
            "var": "Metode Analisis Kuantitatif",
            "body": """
PLS-SEM adalah metode analisis multivariat yang digunakan untuk menguji model
struktural dengan variabel laten. Metode ini dipilih karena kemampuannya menangani
model kompleks dengan ukuran sampel yang lebih kecil dibandingkan CB-SEM
(Covariance-Based SEM), serta cocok untuk penelitian prediktif dan eksploratoris
(Hair et al., 2022).

Dalam penelitian ini, PLS-SEM digunakan untuk menguji pengaruh simultan tiga variabel
independen (X1, X2, X3) terhadap Konsistensi Mutu Produksi (Y).
            """,
            "relevance": "Dasar penentuan bobot IQLS (ISO 25%, IATF 20%, Eng.Lifecycle 35%, Konsistensi 20%), rekomendasi otomatis, dan narasi dominansi Engineering Lifecycle.",
            "plssem": True
        },
        {
            "id": "F",
            "title": "Mixed Methods — Sequential Explanatory Design",
            "color": "#ff6b35",
            "icon": "🔬",
            "var": "Desain Penelitian",
            "body": """
Sequential Explanatory Design (Creswell & Creswell, 2018) adalah desain penelitian
campuran dua fase: fase pertama adalah pengumpulan dan analisis data kuantitatif
(PLS-SEM), yang kemudian dilanjutkan dengan fase kedua berupa pengumpulan data
kualitatif (wawancara mendalam) untuk memperdalam, mengkontekstualisasikan, dan
menjelaskan hasil kuantitatif.

Pendekatan ini dipilih karena hasil PLS-SEM memerlukan penjelasan kontekstual
dari para praktisi dan pemangku kepentingan di lapangan — sesuatu yang tidak dapat
dijawab oleh angka semata.
            """,
            "relevance": "Modul Data Wawancara, input narasumber, kategorisasi temuan kualitatif, key insights, dan summary per kategori."
        },
        {
            "id": "G",
            "title": "PDCA — Plan-Do-Check-Act / Continuous Improvement",
            "color": "#a78bfa",
            "icon": "🔄",
            "var": "Kerangka Perbaikan",
            "body": """
Siklus PDCA (Deming Cycle) adalah kerangka perbaikan berkelanjutan yang menjadi
fondasi sistem manajemen mutu modern. Siklus ini mendorong organisasi untuk
merencanakan tindakan perbaikan (Plan), mengimplementasikannya (Do),
memverifikasi hasilnya (Check), dan menstandarisasi atau menyesuaikan (Act).

Dalam konteks produksi kendaraan, PDCA diterapkan pada setiap batch produksi
sebagai mekanisme umpan balik untuk mereduksi defect dan meningkatkan konsistensi.
            """,
            "relevance": "Monitoring defect antar batch, corrective action pada evaluasi batch, rekomendasi otomatis berbasis skor rendah, dan siklus evaluasi periodik."
        },
        {
            "id": "H",
            "title": "Root Cause Analysis & Defect Prevention",
            "color": "#ff3366",
            "icon": "🔍",
            "var": "Alat Analisis Kualitas",
            "body": """
Root Cause Analysis (RCA) adalah metodologi untuk mengidentifikasi akar penyebab
fundamental dari defect, rework, atau kegagalan produksi — bukan sekadar menangani
gejalanya. Teknik yang umum digunakan meliputi Fishbone Diagram (Ishikawa),
5 Whys, dan FMEA (Failure Mode and Effects Analysis).

Defect prevention menekankan bahwa lebih baik mencegah terjadinya cacat sejak
desain dan proses perencanaan daripada mendeteksi dan memperbaikinya setelah
produksi berlangsung.
            """,
            "relevance": "Evaluasi batch, defect per tahap produksi, Pareto chart, input root cause dan corrective action, serta rekomendasi otomatis pada modul Integrated Quality Score."
        },
    ]

    for th in theories:
        c = th["color"]
        h = c.lstrip('#')
        rv, gv, bv = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

        with st.expander(f"{th['icon']}  {th['id']}. {th['title']}", expanded=False):
            st.markdown(f"""
            <div style="display:inline-block; padding:0.2rem 0.75rem; margin-bottom:0.9rem;
                        background:rgba({rv},{gv},{bv},0.12);
                        border:1px solid rgba({rv},{gv},{bv},0.4);
                        border-radius:5px; font-family:'Rajdhani',sans-serif;
                        font-size:0.72rem; font-weight:700; color:{c};
                        letter-spacing:1.5px; text-transform:uppercase;">
                {th['var']}
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="font-size:0.87rem; color:#c5d5e8; line-height:1.75;
                        padding:0 0.25rem; margin-bottom:1rem;">
                {th['body'].strip()}
            </div>
            """, unsafe_allow_html=True)

            # PLS-SEM result table
            if th.get("plssem"):
                st.markdown("**Ringkasan Hasil Model PLS-SEM:**")
                col1, col2 = st.columns([2, 1])
                with col1:
                    rows = [
                        ("ISO 9001 (X1) → Konsistensi Mutu (Y)",            "0,318", "#00d4ff", "Signifikan"),
                        ("IATF 16949 (X2) → Konsistensi Mutu (Y)",          "0,217", "#0066ff", "Signifikan"),
                        ("Engineering Lifecycle (X3) → Konsistensi Mutu (Y)","0,532", "#00ff88", "Dominan ⭐"),
                    ]
                    for path, coef, clr, label in rows:
                        st.markdown(f"""
                        <div style="display:flex; justify-content:space-between; align-items:center;
                                    padding:0.45rem 0.75rem; margin-bottom:0.3rem;
                                    background:#111827; border-radius:6px;
                                    border-left:3px solid {clr};">
                            <span style="font-size:0.82rem; color:#c5d5e8;">{path}</span>
                            <span style="font-family:'Rajdhani',sans-serif; font-size:1rem;
                                         font-weight:700; color:{clr}; margin-left:1rem;">
                                {coef}
                            </span>
                            <span style="font-size:0.7rem; color:{clr}; margin-left:0.5rem;
                                         border:1px solid {clr}44; padding:1px 6px;
                                         border-radius:4px;">{label}</span>
                        </div>
                        """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div style="text-align:center; padding:1rem; background:#111827;
                                border:1px solid rgba(255,215,0,0.3); border-radius:8px; height:100%;">
                        <div style="font-size:0.68rem; color:#7a9bb5; letter-spacing:1px;
                                    text-transform:uppercase; margin-bottom:0.4rem;">R-Square</div>
                        <div style="font-family:'Rajdhani',sans-serif; font-size:2.5rem;
                                    font-weight:700; color:#ffd700; line-height:1;">0,729</div>
                        <div style="font-size:0.72rem; color:#7a9bb5; margin-top:0.4rem;">
                            72,9% varians Y<br>dijelaskan model
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="padding:0.55rem 0.9rem; background:rgba({rv},{gv},{bv},0.07);
                        border-left:3px solid {c}; border-radius:0 6px 6px 0; margin-top:0.5rem;">
                <span style="font-size:0.7rem; color:{c}; font-weight:700;
                             letter-spacing:1px; text-transform:uppercase;">
                    Relevansi ke Dashboard:
                </span>
                <span style="font-size:0.83rem; color:#c5d5e8; margin-left:0.5rem;">
                    {th['relevance']}
                </span>
            </div>
            """, unsafe_allow_html=True)

    # ── Mapping Teori-Modul ────────────────────────────────
    st.markdown("---")
    st.markdown("### 🗺️ Hubungan Teori dengan Modul Dashboard")
    st.markdown("<br>", unsafe_allow_html=True)

    mapping = [
        ("Quality 4.0",                      "Digital monitoring, KPI, analytics",         "Semua Modul",                         "IQLS Score, Rekomendasi Otomatis"),
        ("ISO 9001:2015",                     "Dokumentasi, Audit, Korektif, CI",            "Modul ISO 9001",                      "Skor X1, Radar Chart, Trend"),
        ("IATF 16949:2016",                   "Defect Prevention, Supplier Quality",         "Modul IATF 16949",                    "Skor X2, Alert Supplier"),
        ("Engineering Lifecycle",             "Design/Change Control, V&V, Traceability",    "Modul Engineering Lifecycle",         "Skor X3, Maturity Level, Area Kritis"),
        ("PLS-SEM",                           "Koefisien jalur, R-Square, dominansi",        "Integrated Quality Score",            "Bobot IQLS, Interpretasi Skor"),
        ("Mixed Methods Seq. Explanatory",    "Kuantitatif + Kualitatif",                    "Data Wawancara",                      "Insight, Kategorisasi Temuan"),
        ("PDCA / Continuous Improvement",     "Plan-Do-Check-Act",                           "Evaluasi Batch, Rekomendasi",         "Defect Trend, Corrective Action"),
        ("Root Cause Analysis",               "Analisis akar penyebab defect",               "Evaluasi Batch, Pareto Chart",        "Defect per Tahap, Top Defect"),
    ]

    header_cols = st.columns([2, 2.5, 2.5, 2.5])
    for col, h in zip(header_cols, ["Teori", "Konsep Utama", "Modul Dashboard", "Output Evaluasi"]):
        col.markdown(f"""
        <div style="padding:0.5rem 0.75rem; background:#0d1321;
                    border-bottom:2px solid #00d4ff; font-family:'Rajdhani',sans-serif;
                    font-size:0.85rem; font-weight:700; color:#00d4ff;
                    letter-spacing:1px; text-transform:uppercase;">
            {h}
        </div>
        """, unsafe_allow_html=True)

    for i, (teori, konsep, modul, output) in enumerate(mapping):
        bg = "#111827" if i % 2 == 0 else "#0d1321"
        row = st.columns([2, 2.5, 2.5, 2.5])
        cells = [teori, konsep, modul, output]
        colors = ["#00d4ff", "#c5d5e8", "#ffd700", "#00ff88"]
        for col, text, clr in zip(row, cells, colors):
            col.markdown(f"""
            <div style="padding:0.5rem 0.75rem; background:{bg};
                        border-bottom:1px solid rgba(0,212,255,0.08);
                        font-size:0.82rem; color:{clr}; line-height:1.4;">
                {text}
            </div>
            """, unsafe_allow_html=True)

    # ── Referensi Akademik ─────────────────────────────────
    st.markdown("---")
    st.markdown("### 📄 Referensi Akademik")
    st.markdown("<br>", unsafe_allow_html=True)

    references = [
        ("ISO",       "2015", "ISO 9001:2015 Quality management systems — Requirements.", "Standar Internasional", "#00d4ff"),
        ("IATF",      "2016", "IATF 16949:2016 Quality management system requirements for automotive production and relevant service parts organizations.", "Standar Otomotif", "#0066ff"),
        ("INCOSE",    "2023", "Systems Engineering Handbook: A Guide for System Life Cycle Processes and Activities (5th ed.).", "Handbook", "#00ff88"),
        ("Creswell & Creswell", "2018", "Research Design: Qualitative, Quantitative, and Mixed Methods Approaches.", "Metodologi Penelitian", "#ff6b35"),
        ("Creswell & Plano Clark", "2018", "Designing and Conducting Mixed Methods Research.", "Mixed Methods", "#ff6b35"),
        ("Hair et al.", "2022", "A Primer on Partial Least Squares Structural Equation Modeling (PLS-SEM).", "PLS-SEM", "#ffd700"),
        ("Antony, J.", "2023", "Quality 4.0 and operational excellence: A review of current practices and future directions.", "Quality 4.0", "#a78bfa"),
        ("Cooper & Vigon", "2001", "Life Cycle Engineering: Definitions and Strategy.", "Engineering Lifecycle", "#ff3366"),
    ]

    for i, (author, year, title, tag, color) in enumerate(references):
        h = color.lstrip('#')
        rv2, gv2, bv2 = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        st.markdown(f"""
        <div style="display:flex; align-items:flex-start; gap:1rem;
                    padding:0.75rem 1rem; margin-bottom:0.4rem;
                    background:#111827; border-radius:8px;
                    border-left:3px solid {color};">
            <span style="font-family:'Rajdhani',sans-serif; font-size:1.1rem;
                          font-weight:700; color:{color}; min-width:1.5rem;">
                [{i+1}]
            </span>
            <div style="flex:1;">
                <span style="font-size:0.85rem; color:#e8edf5;">
                    <b style="color:#c5d5e8;">{author}</b> ({year}). <i>{title}</i>
                </span>
                <span style="display:inline-block; margin-left:0.5rem;
                             background:rgba({rv2},{gv2},{bv2},0.15);
                             border:1px solid rgba({rv2},{gv2},{bv2},0.4);
                             border-radius:4px; padding:1px 7px;
                             font-size:0.68rem; color:{color};
                             font-family:'Rajdhani',sans-serif; font-weight:700;
                             letter-spacing:1px; vertical-align:middle;">
                    {tag}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Footer note ────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="padding:0.75rem 1rem; background:rgba(0,0,0,0.3);
                border:1px solid rgba(255,255,255,0.06); border-radius:8px;
                text-align:center; font-size:0.75rem; color:#3d5470;">
        IQLE Platform — Prototype Akademik Magister Teknik &nbsp;|&nbsp;
        PT Pindad (Persero) &nbsp;|&nbsp; Quality 4.0 Dashboard
    </div>
    """, unsafe_allow_html=True)
