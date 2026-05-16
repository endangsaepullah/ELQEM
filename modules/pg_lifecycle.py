import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.database import fetchall, fetchone, execute, get_category, get_lifecycle_maturity
from utils.styles import section_header, plotly_layout
from utils.auth import is_admin
from datetime import date

IND = {
    'design_control':               'Design Control',
    'change_control':               'Change Control',
    'verification_validation':      'Verification & Validation',
    'integration_process':          'Integration Process',
    'traceability':                 'Traceability',
    'design_change_communication':  'Communication of Design Change',
}

MAT_COLOR = {
    'Initial':    '#ff3366',
    'Developing': '#ff6b35',
    'Defined':    '#ffd700',
    'Managed':    '#00d4ff',
    'Optimized':  '#00ff88',
}


def show():
    section_header("Engineering Lifecycle", "Faktor Dominan Konsistensi Mutu (PLS-SEM) ⭐", "⚙️")

    st.markdown("""
    <div style="padding:.65rem 1rem; background:rgba(0,255,136,.07);
                border:1px solid rgba(0,255,136,.3); border-radius:8px; margin-bottom:1rem;
                font-size:.83rem; color:#7a9bb5;">
        <b style="color:#00ff88;">ℹ️ RESEARCH NOTE:</b>
        Engineering Lifecycle (X3) adalah faktor paling dominan mempengaruhi
        Konsistensi Mutu Produksi (Y) berdasarkan hasil analisis PLS-SEM.
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📈 Monitoring", "➕ Input Evaluasi", "📋 Riwayat"])
    df = pd.DataFrame(fetchall(conn, "SELECT * FROM engineering_lifecycle ORDER BY eval_date DESC"))

    with tab1:
        if df.empty:
            st.info("Belum ada data.")
        else:
            latest = df.iloc[0]
            maturity = latest['maturity_level']
            mc = MAT_COLOR.get(maturity, '#7a9bb5')

            col_m, col_r = st.columns([1, 2])

            with col_m:
                st.markdown(f"""
                <div style="text-align:center; padding:1.5rem;
                            background:{mc}11; border:2px solid {mc}44; border-radius:12px;">
                    <div style="font-size:.65rem; color:#7a9bb5; letter-spacing:2px;
                                text-transform:uppercase;">Maturity Level</div>
                    <div style="font-family:'Rajdhani',sans-serif; font-size:3rem;
                                font-weight:700; color:{mc}; margin:.4rem 0;">
                        {latest['average_score']:.1f}
                    </div>
                    <div style="font-family:'Rajdhani',sans-serif; font-size:1.1rem;
                                font-weight:600; color:{mc};">{maturity}</div>
                </div>
                <br>
                """, unsafe_allow_html=True)

                for lvl in ['Optimized','Managed','Defined','Developing','Initial']:
                    c = MAT_COLOR[lvl]
                    active = (lvl == maturity)
                    bg = f"background:{c}22; border-left:3px solid {c};" if active else \
                         "background:#111827; border-left:3px solid transparent;"
                    st.markdown(f"""
                    <div style="{bg} padding:.35rem .75rem; border-radius:4px;
                                margin-bottom:.25rem; font-family:Rajdhani; font-size:.85rem;
                                color:{c if active else '#4a6fa5'}; font-weight:{'700' if active else '400'};">
                        {'▶ ' if active else '  '}{lvl}
                    </div>
                    """, unsafe_allow_html=True)

            with col_r:
                st.markdown("#### 🕸️ Radar Chart Engineering Lifecycle")
                labels = list(IND.values())
                vals   = [latest[k] for k in IND]
                ref    = [75]*6
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=ref+[ref[0]], theta=labels+[labels[0]], fill='toself', name='Target 75',
                    line=dict(color='#ffd700', width=1, dash='dot'),
                    fillcolor='rgba(255,215,0,0.04)'
                ))
                fig.add_trace(go.Scatterpolar(
                    r=vals+[vals[0]], theta=labels+[labels[0]], fill='toself', name='Aktual',
                    line=dict(color='#00ff88', width=2),
                    fillcolor='rgba(0,255,136,0.1)'
                ))
                lay = plotly_layout()
                lay.update(polar=dict(
                    radialaxis=dict(visible=True, range=[0,100],
                                   gridcolor='rgba(0,255,136,0.1)', tickfont=dict(size=9)),
                    bgcolor='rgba(0,0,0,0)'
                ), height=370)
                fig.update_layout(**lay)
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.markdown("#### ⚠️ Area Kritis (Skor < 70)")
            critical = [(IND[k], latest[k]) for k in IND if latest[k] < 70]
            if critical:
                for label, val in critical:
                    st.markdown(f"""
                    <div style="padding:.6rem 1rem; background:rgba(255,51,102,.1);
                                border:1px solid rgba(255,51,102,.3); border-radius:6px; margin-bottom:.4rem;">
                        <b style="color:#ff3366;">⚠️ {label}</b>
                        <span style="float:right; color:#ff3366; font-family:Rajdhani; font-size:1.05rem;">
                            {val:.1f}/100
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ Semua indikator ≥ 70 — tidak ada area kritis.")

            st.markdown("#### 📈 Trend per Indikator")
            t = df[::-1]
            clrs = ['#00d4ff','#ff3366','#00ff88','#ffd700','#ff6b35','#a78bfa']
            fig2 = go.Figure()
            for i,(k,l) in enumerate(IND.items()):
                fig2.add_trace(go.Scatter(
                    x=t['eval_date'], y=t[k], mode='lines+markers', name=l,
                    line=dict(color=clrs[i], width=1.5), marker=dict(size=5), opacity=0.85
                ))
            fig2.add_trace(go.Scatter(
                x=t['eval_date'], y=t['average_score'], mode='lines+markers', name='Rata-rata',
                line=dict(color='white', width=2.5), marker=dict(size=8)
            ))
            lay2 = plotly_layout()
            lay2.update(height=280, yaxis=dict(**lay2['yaxis'], range=[0,100]))
            fig2.update_layout(**lay2)
            st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        if not is_admin():
            st.warning("⛔ Hanya Admin.")
        else:
            batch_list = pd.DataFrame(fetchall(conn, "SELECT batch_number FROM batch_production ORDER BY production_date DESC"))
            opts = ["(Tidak terkait batch)"] + list(batch_list['batch_number'])
            with st.form("lc_form"):
                c1,c2,c3 = st.columns(3)
                ed   = c1.date_input("Tanggal", value=date.today())
                bn   = c2.selectbox("Batch", opts)
                evlr = c3.text_input("Evaluator")
                ca, cb = st.columns(2)
                scores = {}
                for i,(k,l) in enumerate(IND.items()):
                    col = ca if i < 3 else cb
                    with col:
                        scores[k] = st.slider(l, 0, 100, 70, key=f"lc_{k}")
                notes = st.text_area("Catatan")
                if st.form_submit_button("💾 Simpan", use_container_width=True, type="primary"):
                    avg = sum(scores.values())/len(scores)
                    mat = get_lifecycle_maturity(avg)
                    bv  = None if bn.startswith("(") else bn
                    execute("""
                        INSERT INTO engineering_lifecycle
                        (eval_date,batch_number,design_control,change_control,
                         verification_validation,integration_process,traceability,
                         design_change_communication,average_score,maturity_level,evaluator,notes)
                        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (str(ed),bv,scores['design_control'],scores['change_control'],
                         scores['verification_validation'],scores['integration_process'],
                         scores['traceability'],scores['design_change_communication'],
                         avg,mat,evlr,notes))
                    st.success(f"✅ Tersimpan! Skor: {avg:.1f} | Maturity: {mat}")
                    st.rerun()

    with tab3:
        if not df.empty:
            cols_show = ['eval_date','batch_number','design_control','change_control',
                         'verification_validation','integration_process','traceability',
                         'design_change_communication','average_score','maturity_level','evaluator']
            disp = df[cols_show].copy()
            disp.columns = ['Tanggal','Batch','Design Ctrl','Change Ctrl','V&V',
                            'Integration','Traceability','Comm.Change','Avg','Maturity','Evaluator']
            st.dataframe(disp, use_container_width=True, hide_index=True)
            if is_admin():
                st.download_button("📥 Export CSV", disp.to_csv(index=False).encode(), "eng_lifecycle.csv", "text/csv")
        else:
            st.info("Belum ada data.")
