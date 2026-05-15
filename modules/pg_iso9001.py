import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.database import get_connection, get_category
from utils.styles import section_header, plotly_layout, category_banner
from utils.auth import is_admin
from datetime import date

IND = {
    'process_documentation': 'Dokumentasi Proses',
    'process_control':       'Pengendalian Proses',
    'internal_audit':        'Audit Internal',
    'corrective_action':     'Tindakan Korektif',
    'continuous_improvement':'Continuous Improvement',
}


def show():
    section_header("Modul ISO 9001", "Quality Management System Evaluation", "📊")
    tab1, tab2, tab3 = st.tabs(["📈 Monitoring", "➕ Input Evaluasi", "📋 Riwayat"])

    conn = get_connection()
    df = pd.read_sql("SELECT * FROM iso9001_evaluation ORDER BY eval_date DESC", conn)

    with tab1:
        if df.empty:
            st.info("Belum ada data. Silakan input melalui tab 'Input Evaluasi'.")
        else:
            latest = df.iloc[0]
            cols = st.columns(6)
            lbls = list(IND.values()) + ["Rata-rata"]
            vals = [latest[k] for k in IND] + [latest['average_score']]
            for i, (col, l, v) in enumerate(zip(cols, lbls, vals)):
                col.metric(l[:14], f"{v:.1f}")

            st.markdown("---")
            c1, c2 = st.columns(2)

            with c1:
                st.markdown("#### 🕸️ Radar Chart")
                labels = list(IND.values())
                vals_r = [latest[k] for k in IND]
                fig = go.Figure(go.Scatterpolar(
                    r=vals_r+[vals_r[0]], theta=labels+[labels[0]],
                    fill='toself', name='ISO 9001',
                    line=dict(color='#00d4ff', width=2),
                    fillcolor='rgba(0,212,255,0.12)'
                ))
                lay = plotly_layout()
                lay.update(polar=dict(
                    radialaxis=dict(visible=True, range=[0,100],
                                   gridcolor='rgba(0,212,255,0.12)', tickfont=dict(size=9)),
                    bgcolor='rgba(0,0,0,0)'
                ), height=340)
                fig.update_layout(**lay)
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                st.markdown("#### 📈 Trend Skor")
                t = df[::-1]
                fig2 = go.Figure(go.Scatter(
                    x=t['eval_date'], y=t['average_score'],
                    mode='lines+markers+text',
                    line=dict(color='#00d4ff', width=2),
                    marker=dict(size=9, color='#00d4ff'),
                    text=[f"{v:.1f}" for v in t['average_score']],
                    textposition='top center', textfont=dict(size=9),
                    fill='tozeroy', fillcolor='rgba(0,212,255,0.06)'
                ))
                fig2.add_hline(y=75, line_dash="dash", line_color="#ffd700",
                               annotation_text="Target 75", annotation_font_color="#ffd700")
                lay2 = plotly_layout()
                lay2.update(height=340, yaxis=dict(**lay2['yaxis'], range=[0,100]))
                fig2.update_layout(**lay2)
                st.plotly_chart(fig2, use_container_width=True)

            category_banner(latest['average_score'], latest['category'])

    with tab2:
        if not is_admin():
            st.warning("⛔ Hanya Admin yang dapat menginput data.")
        else:
            batch_list = pd.read_sql("SELECT batch_number FROM batch_production ORDER BY production_date DESC", conn)
            opts = ["(Tidak terkait batch)"] + list(batch_list['batch_number'])
            with st.form("iso_form"):
                c1,c2,c3 = st.columns(3)
                ed   = c1.date_input("Tanggal Evaluasi", value=date.today())
                bn   = c2.selectbox("Batch", opts)
                evlr = c3.text_input("Evaluator")
                st.markdown("##### Skor Indikator (0–100)")
                ca, cb = st.columns(2)
                scores = {}
                items = list(IND.items())
                for i,(k,l) in enumerate(items):
                    col = ca if i < 3 else cb
                    with col:
                        scores[k] = st.slider(l, 0, 100, 70, key=f"iso_{k}")
                notes = st.text_area("Catatan")
                if st.form_submit_button("💾 Simpan", use_container_width=True, type="primary"):
                    avg = sum(scores.values())/len(scores)
                    cat = get_category(avg)
                    bv  = None if bn.startswith("(") else bn
                    conn.execute("""
    conn.commit()
                        INSERT INTO iso9001_evaluation
                        (eval_date,batch_number,process_documentation,process_control,
                         internal_audit,corrective_action,continuous_improvement,
                         average_score,category,evaluator,notes)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                        (str(ed),bv,scores['process_documentation'],scores['process_control'],
                         scores['internal_audit'],scores['corrective_action'],
                         scores['continuous_improvement'],avg,cat,evlr,notes))
                    conn.commit()
                    st.success(f"✅ Tersimpan! Skor: {avg:.1f} ({cat})")
                    st.rerun()

    with tab3:
        if not df.empty:
            disp = df[['eval_date','batch_number','process_documentation','process_control',
                        'internal_audit','corrective_action','continuous_improvement',
                        'average_score','category','evaluator']].copy()
            disp.columns = ['Tanggal','Batch','Dok.Proses','Kendali','Audit','Korektif','CI','Avg','Kategori','Evaluator']
            st.dataframe(disp, use_container_width=True, hide_index=True)
            if is_admin():
                st.download_button("📥 Export CSV", disp.to_csv(index=False).encode(), "iso9001.csv", "text/csv")
        else:
            st.info("Belum ada data.")
    conn.close()
