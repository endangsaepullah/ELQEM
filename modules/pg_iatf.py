import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.database import get_connection, get_category
from utils.styles import section_header, plotly_layout, category_banner
from utils.auth import is_admin
from datetime import date

IND = {
    'risk_based_thinking':   'Risk-Based Thinking',
    'defect_prevention':     'Defect Prevention',
    'supplier_quality':      'Supplier Quality',
    'continuous_improvement':'Continuous Improvement',
}


def show():
    section_header("Modul IATF 16949", "Automotive Quality Management System", "🏭")
    tab1, tab2, tab3 = st.tabs(["📈 Monitoring", "➕ Input Evaluasi", "📋 Riwayat"])

    conn = get_connection()
    df = pd.read_sql("SELECT * FROM iatf16949_evaluation ORDER BY eval_date DESC", conn)

    with tab1:
        if df.empty:
            st.info("Belum ada data.")
        else:
            latest = df.iloc[0]
            c1,c2,c3,c4,c5 = st.columns(5)
            for col, k, l in zip([c1,c2,c3,c4], IND.keys(), IND.values()):
                col.metric(l[:18], f"{latest[k]:.1f}")
            c5.metric("Rata-rata", f"{latest['average_score']:.1f}")

            if latest['supplier_quality'] < 70:
                st.warning(f"⚠️ Supplier Quality rendah ({latest['supplier_quality']:.1f}/100). Perlu tindakan segera.")

            st.markdown("---")
            c1, c2 = st.columns(2)

            with c1:
                st.markdown("#### 🕸️ Radar Chart")
                labels = list(IND.values())
                vals = [latest[k] for k in IND]
                fig = go.Figure(go.Scatterpolar(
                    r=vals+[vals[0]], theta=labels+[labels[0]],
                    fill='toself', name='IATF 16949',
                    line=dict(color='#0066ff', width=2),
                    fillcolor='rgba(0,102,255,0.12)'
                ))
                lay = plotly_layout()
                lay.update(polar=dict(
                    radialaxis=dict(visible=True, range=[0,100],
                                   gridcolor='rgba(0,102,255,0.12)', tickfont=dict(size=9)),
                    bgcolor='rgba(0,0,0,0)'
                ), height=340)
                fig.update_layout(**lay)
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                st.markdown("#### 📊 Rata-rata per Indikator")
                avgs = {l: df[k].mean() for k, l in IND.items()}
                fig2 = go.Figure(go.Bar(
                    x=list(avgs.keys()), y=list(avgs.values()),
                    marker=dict(color=['#00d4ff','#ff6b35','#ffd700','#00ff88'], opacity=0.85),
                    text=[f"{v:.1f}" for v in avgs.values()], textposition='outside'
                ))
                lay2 = plotly_layout()
                lay2.update(height=340, yaxis=dict(**lay2['yaxis'], range=[0,110]))
                fig2.update_layout(**lay2)
                st.plotly_chart(fig2, use_container_width=True)

            category_banner(latest['average_score'], latest['category'])

    with tab2:
        if not is_admin():
            st.warning("⛔ Hanya Admin.")
        else:
            batch_list = pd.read_sql("SELECT batch_number FROM batch_production ORDER BY production_date DESC", conn)
            opts = ["(Tidak terkait batch)"] + list(batch_list['batch_number'])
            with st.form("iatf_form"):
                c1,c2,c3 = st.columns(3)
                ed   = c1.date_input("Tanggal", value=date.today())
                bn   = c2.selectbox("Batch", opts)
                evlr = c3.text_input("Evaluator")
                ca, cb = st.columns(2)
                scores = {}
                for i,(k,l) in enumerate(IND.items()):
                    col = ca if i < 2 else cb
                    with col:
                        scores[k] = st.slider(l, 0, 100, 70, key=f"iatf_{k}")
                notes = st.text_area("Catatan")
                if st.form_submit_button("💾 Simpan", use_container_width=True, type="primary"):
                    avg = sum(scores.values())/len(scores)
                    bv  = None if bn.startswith("(") else bn
                    _cur = conn.cursor(); _cur.execute("""
                    conn.commit()
                    _cur.close()
                        INSERT INTO iatf16949_evaluation
                        (eval_date,batch_number,risk_based_thinking,defect_prevention,
                         supplier_quality,continuous_improvement,average_score,category,evaluator,notes)
                        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (str(ed),bv,scores['risk_based_thinking'],scores['defect_prevention'],
                         scores['supplier_quality'],scores['continuous_improvement'],
                         avg,get_category(avg),evlr,notes))
                    conn.commit()
                    st.success(f"✅ Tersimpan! Skor: {avg:.1f}")
                    st.rerun()

    with tab3:
        if not df.empty:
            disp = df[['eval_date','batch_number','risk_based_thinking','defect_prevention',
                        'supplier_quality','continuous_improvement','average_score','category','evaluator']].copy()
            disp.columns = ['Tanggal','Batch','Risk Thinking','Defect Prev.','Supplier Q.','CI','Avg','Kategori','Evaluator']
            st.dataframe(disp, use_container_width=True, hide_index=True)
            if is_admin():
                st.download_button("📥 Export CSV", disp.to_csv(index=False).encode(), "iatf16949.csv", "text/csv")
        else:
            st.info("Belum ada data.")
    conn.close()
