import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.database import get_connection, fetchall, fetchone, get_category
from utils.styles import section_header, plotly_layout

WEIGHTS = {'ISO 9001 (X1)': 0.25, 'IATF 16949 (X2)': 0.20,
           'Engineering Lifecycle (X3)': 0.35, 'Konsistensi Mutu (Y)': 0.20}

RECS = {
    'low_process_documentation':     ('ISO 9001',              '#00d4ff', '📄 Tingkatkan dokumentasi SOP — pastikan selalu diperbarui setiap ada perubahan proses.'),
    'low_internal_audit':            ('ISO 9001',              '#00d4ff', '🔍 Jadwalkan audit internal rutin minimal 2× per tahun secara konsisten.'),
    'low_corrective_action_iso':     ('ISO 9001',              '#00d4ff', '🔧 Implementasikan sistem CAPA yang terstruktur untuk setiap temuan.'),
    'low_supplier_quality':          ('IATF 16949',            '#0066ff', '🏭 Tingkatkan kualifikasi dan audit supplier secara berkala.'),
    'low_risk_based_thinking':       ('IATF 16949',            '#0066ff', '⚠️ Lakukan risk assessment berkala pada seluruh proses produksi.'),
    'low_defect_prevention':         ('IATF 16949',            '#0066ff', '🛡️ Implementasikan FMEA pada proses kritis.'),
    'low_change_control':            ('Eng. Lifecycle ⭐',     '#00ff88', '🔄 Perkuat change control — setiap perubahan desain wajib melalui ECO.'),
    'low_verification_validation':   ('Eng. Lifecycle ⭐',     '#00ff88', '✅ Buat test plan komprehensif sebelum produksi batch baru.'),
    'low_design_change_comm':        ('Eng. Lifecycle ⭐',     '#00ff88', '📢 Implementasikan sistem komunikasi perubahan desain antar departemen.'),
    'low_traceability':              ('Eng. Lifecycle ⭐',     '#00ff88', '🔗 Bangun sistem traceability material dari supplier hingga produk jadi.'),
    'low_inter_batch_stability':     ('Konsistensi Mutu',      '#ffd700', '📊 Gunakan SPC untuk monitoring stabilitas proses antar batch.'),
    'low_spec_conformance':          ('Konsistensi Mutu',      '#ffd700', '📋 Review dan perketat acceptance criteria pada final inspection.'),
    'high_defect_rate':              ('Batch Quality',         '#ff3366', '📉 Defect rate >10% — lakukan root cause analysis menyeluruh segera.'),
}


def show():
    section_header("Integrated Quality Score", "Total Quality Lifecycle Score & Rekomendasi Otomatis", "🎯")

    conn = get_connection()
    iso_r  = pd.DataFrame(fetchall(conn, "SELECT * FROM iso9001_evaluation        ORDER BY eval_date DESC LIMIT 1"))
    iatf_r = pd.DataFrame(fetchall(conn, "SELECT * FROM iatf16949_evaluation      ORDER BY eval_date DESC LIMIT 1"))
    lc_r   = pd.DataFrame(fetchall(conn, "SELECT * FROM engineering_lifecycle     ORDER BY eval_date DESC LIMIT 1"))
    qc_r   = pd.DataFrame(fetchall(conn, "SELECT * FROM quality_consistency       ORDER BY eval_date DESC LIMIT 1"))
    b_r    = pd.DataFrame(fetchall(conn, "SELECT defect_rate FROM batch_production ORDER BY production_date DESC LIMIT 3"))
    conn.close()

    iso  = float(iso_r.iloc[0]['average_score'])  if not iso_r.empty  else 0
    iatf = float(iatf_r.iloc[0]['average_score']) if not iatf_r.empty else 0
    lc   = float(lc_r.iloc[0]['average_score'])   if not lc_r.empty   else 0
    qc   = float(qc_r.iloc[0]['average_score'])   if not qc_r.empty   else 0
    iqls = round(iso*0.25 + iatf*0.20 + lc*0.35 + qc*0.20, 1)
    cat  = get_category(iqls)

    cat_c = {"Sangat Baik":"#00ff88","Baik":"#00d4ff","Cukup":"#ffd700","Perlu Perbaikan":"#ff3366"}
    mc = cat_c.get(cat,"#7a9bb5")

    col_l, col_r = st.columns([1, 2])

    with col_l:
        st.markdown(f"""
        <div style="text-align:center; padding:1.75rem 1rem;
                    background:{mc}11; border:2px solid {mc}44; border-radius:14px;">
            <div style="font-size:.62rem; color:#7a9bb5; letter-spacing:3px;
                        text-transform:uppercase; margin-bottom:.4rem;">
                TOTAL QUALITY LIFECYCLE SCORE
            </div>
            <div style="font-family:'Rajdhani',sans-serif; font-size:4.5rem;
                        font-weight:700; color:{mc}; line-height:1;">{iqls}</div>
            <div style="font-family:'Rajdhani',sans-serif; font-size:1.3rem;
                        font-weight:600; color:{mc}; margin-top:.3rem;">{cat}</div>
        </div>
        <br>
        """, unsafe_allow_html=True)

        score_items = [
            ('ISO 9001 (X1)',             iso,  '#00d4ff', 0.25),
            ('IATF 16949 (X2)',           iatf, '#0066ff', 0.20),
            ('Engineering Lifecycle (X3)',lc,   '#00ff88', 0.35),
            ('Konsistensi Mutu (Y)',      qc,   '#ffd700', 0.20),
        ]
        for name, score, color, w in score_items:
            wv = score * w
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center;
                        padding:.4rem 0; border-bottom:1px solid rgba(255,255,255,0.05);">
                <span style="font-size:.75rem; color:#7a9bb5;">{name}</span>
                <span style="font-family:Rajdhani; font-size:.9rem; color:{color}; font-weight:600;">
                    {score:.1f}×{w} = <b style="color:white">{wv:.1f}</b>
                </span>
            </div>
            """, unsafe_allow_html=True)

        cats = [("0–59","Perlu Perbaikan","#ff3366"),("60–74","Cukup","#ffd700"),
                ("75–84","Baik","#00d4ff"),("85–100","Sangat Baik","#00ff88")]
        st.markdown("<br>", unsafe_allow_html=True)
        for rng, lbl, c in cats:
            active = (lbl == cat)
            st.markdown(f"""
            <div style="text-align:center; padding:.35rem; border-radius:5px; margin-bottom:.25rem;
                        background:{c+'22' if active else '#111827'};
                        border:1px solid {c if active else 'transparent'};">
                <span style="font-size:.65rem; color:#7a9bb5;">{rng}</span>
                <span style="font-family:Rajdhani; font-size:.8rem; font-weight:700;
                             color:{c}; margin-left:.5rem;">{lbl}</span>
            </div>
            """, unsafe_allow_html=True)

    with col_r:
        # Gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=iqls,
            domain={'x':[0,1],'y':[0,1]},
            title={'text':"IQLS Score",'font':{'color':'#e8edf5','family':'Rajdhani','size':18}},
            gauge={
                'axis':{'range':[0,100],'tickwidth':1,'tickcolor':'#4a6fa5',
                        'tickfont':{'color':'#7a9bb5'}},
                'bar':{'color':mc,'thickness':0.28},
                'bgcolor':'rgba(13,19,33,0.7)',
                'borderwidth':0,
                'steps':[
                    {'range':[0,59],'color':'rgba(255,51,102,0.15)'},
                    {'range':[59,74],'color':'rgba(255,215,0,0.12)'},
                    {'range':[74,84],'color':'rgba(0,212,255,0.12)'},
                    {'range':[84,100],'color':'rgba(0,255,136,0.12)'},
                ],
                'threshold':{'line':{'color':'#ffd700','width':3},'thickness':0.75,'value':75}
            }
        ))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color':'#e8edf5'},
                          height=300, margin=dict(l=20,r=20,t=50,b=10))
        st.plotly_chart(fig, use_container_width=True)

        # Spider chart
        labels = list(WEIGHTS.keys())
        vals   = [iso, iatf, lc, qc]
        fig2 = go.Figure()
        ref = [75]*4
        fig2.add_trace(go.Scatterpolar(
            r=ref+[ref[0]], theta=labels+[labels[0]], fill='toself', name='Target 75',
            line=dict(color='#ffd700',width=1,dash='dot'), fillcolor='rgba(255,215,0,0.04)'
        ))
        h = mc.lstrip('#')
        rv,gv,bv = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        fig2.add_trace(go.Scatterpolar(
            r=vals+[vals[0]], theta=labels+[labels[0]], fill='toself', name='Aktual',
            line=dict(color=mc,width=2.5), fillcolor=f'rgba({rv},{gv},{bv},0.15)'
        ))
        lay = plotly_layout()
        lay.update(polar=dict(
            radialaxis=dict(visible=True, range=[0,100],
                           gridcolor='rgba(255,255,255,0.07)', tickfont=dict(size=9)),
            bgcolor='rgba(0,0,0,0)'
        ), height=300)
        fig2.update_layout(**lay)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 💡 Rekomendasi Otomatis")

    triggers = []
    if not iso_r.empty:
        r = iso_r.iloc[0]
        if r['process_documentation']  < 70: triggers.append('low_process_documentation')
        if r['internal_audit']         < 70: triggers.append('low_internal_audit')
        if r['corrective_action']      < 70: triggers.append('low_corrective_action_iso')
    if not iatf_r.empty:
        r = iatf_r.iloc[0]
        if r['supplier_quality']       < 70: triggers.append('low_supplier_quality')
        if r['risk_based_thinking']    < 70: triggers.append('low_risk_based_thinking')
        if r['defect_prevention']      < 70: triggers.append('low_defect_prevention')
    if not lc_r.empty:
        r = lc_r.iloc[0]
        if r['change_control']                 < 70: triggers.append('low_change_control')
        if r['verification_validation']        < 70: triggers.append('low_verification_validation')
        if r['design_change_communication']    < 70: triggers.append('low_design_change_comm')
        if r['traceability']                   < 70: triggers.append('low_traceability')
    if not b_r.empty and b_r['defect_rate'].mean() > 10:
        triggers.append('high_defect_rate')

    if triggers:
        for key in triggers[:8]:
            module, color, msg = RECS[key]
            st.markdown(f"""
            <div style="padding:.7rem 1rem; background:{color}0f;
                        border-left:3px solid {color}; border-radius:0 6px 6px 0;
                        margin-bottom:.45rem;">
                <div style="font-size:.62rem; color:{color}; letter-spacing:1px;
                            text-transform:uppercase; font-weight:700; margin-bottom:.2rem;">
                    [{module}]
                </div>
                <div style="font-size:.83rem; color:#e8edf5; line-height:1.45;">{msg}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ Semua indikator dalam kondisi baik! Pertahankan performa mutu.")
