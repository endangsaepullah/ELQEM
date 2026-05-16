import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.database import get_connection, get_category
from utils.styles import section_header, plotly_layout, category_banner
from utils.auth import is_admin
from datetime import date

IND = {
    'quality_uniformity':    'Keseragaman Mutu',
    'low_defect_rate':       'Defect Rendah',
    'inter_batch_stability': 'Stabilitas Antar Batch',
    'low_rework_rate':       'Rework Rendah',
    'spec_conformance':      'Kesesuaian Spesifikasi',
}


def show():
    section_header("Konsistensi Mutu", "Quality Consistency & Production Stability", "✅")
    tab1, tab2, tab3 = st.tabs(["📈 Monitoring", "➕ Input Evaluasi", "📋 Riwayat"])

    conn = get_connection()
    df       = pd.read_sql("SELECT * FROM quality_consistency ORDER BY eval_date DESC", conn)
    batch_df = pd.read_sql("SELECT * FROM batch_production ORDER BY production_date",    conn)

    with tab1:
        if df.empty:
            st.info("Belum ada data.")
        else:
            latest = df.iloc[0]
            cols = st.columns(6)
            for i,(k,l) in enumerate(IND.items()):
                cols[i].metric(l[:16], f"{latest[k]:.1f}")
            cols[5].metric("Rata-rata", f"{latest['average_score']:.1f}")

            st.markdown("---")
            c1, c2 = st.columns(2)

            with c1:
                st.markdown("#### 🕸️ Radar Chart")
                labels = list(IND.values())
                vals   = [latest[k] for k in IND]
                fig = go.Figure(go.Scatterpolar(
                    r=vals+[vals[0]], theta=labels+[labels[0]],
                    fill='toself', name='Konsistensi Mutu',
                    line=dict(color='#ffd700', width=2),
                    fillcolor='rgba(255,215,0,0.1)'
                ))
                lay = plotly_layout()
                lay.update(polar=dict(
                    radialaxis=dict(visible=True, range=[0,100],
                                   gridcolor='rgba(255,215,0,0.1)', tickfont=dict(size=9)),
                    bgcolor='rgba(0,0,0,0)'
                ), height=340)
                fig.update_layout(**lay)
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                st.markdown("#### 📊 Batch Consistency Chart")
                if not batch_df.empty:
                    fig2 = go.Figure()
                    fig2.add_trace(go.Bar(x=batch_df['batch_number'], y=batch_df['total_units'],
                                          name='Unit', marker=dict(color='#00d4ff', opacity=0.7)))
                    fig2.add_trace(go.Bar(x=batch_df['batch_number'], y=batch_df['total_defect'],
                                          name='Defect', marker=dict(color='#ff3366', opacity=0.8)))
                    lay2 = plotly_layout()
                    lay2.update(barmode='group', height=340,
                                xaxis=dict(**lay2['xaxis'], tickangle=45, tickfont=dict(size=7)))
                    fig2.update_layout(**lay2)
                    st.plotly_chart(fig2, use_container_width=True)

            st.markdown("#### 📈 Trend Konsistensi")
            t = df[::-1]
            clrs = ['#ffd700','#00d4ff','#00ff88','#ff6b35','#a78bfa']
            fig3 = go.Figure()
            for i,(k,l) in enumerate(IND.items()):
                fig3.add_trace(go.Scatter(x=t['eval_date'], y=t[k], mode='lines+markers', name=l,
                                          line=dict(color=clrs[i], width=1.5), marker=dict(size=5)))
            fig3.add_trace(go.Scatter(x=t['eval_date'], y=t['average_score'], mode='lines+markers',
                                       name='Rata-rata', line=dict(color='white', width=2.5), marker=dict(size=8)))
            lay3 = plotly_layout()
            lay3.update(height=260, yaxis=dict(**lay3['yaxis'], range=[0,100]))
            fig3.update_layout(**lay3)
            st.plotly_chart(fig3, use_container_width=True)

            category_banner(latest['average_score'], latest['category'])

    with tab2:
        if not is_admin():
            st.warning("⛔ Hanya Admin.")
        else:
            opts = ["(Tidak terkait batch)"] + list(batch_df['batch_number']) if not batch_df.empty else ["(Tidak terkait batch)"]
            with st.form("qc_form"):
                c1,c2,c3 = st.columns(3)
                ed   = c1.date_input("Tanggal", value=date.today())
                bn   = c2.selectbox("Batch", opts)
                evlr = c3.text_input("Evaluator")
                ca, cb = st.columns(2)
                scores = {}
                for i,(k,l) in enumerate(IND.items()):
                    col = ca if i < 3 else cb
                    with col:
                        scores[k] = st.slider(l, 0, 100, 70, key=f"qc_{k}")
                notes = st.text_area("Catatan")
                if st.form_submit_button("💾 Simpan", use_container_width=True, type="primary"):
                    avg = sum(scores.values())/len(scores)
                    bv  = None if bn.startswith("(") else bn
                    conn.execute("""
    conn.commit()
                        INSERT INTO quality_consistency
                        (eval_date,batch_number,quality_uniformity,low_defect_rate,
                         inter_batch_stability,low_rework_rate,spec_conformance,
                         average_score,category,evaluator,notes)
                        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (str(ed),bv,scores['quality_uniformity'],scores['low_defect_rate'],
                         scores['inter_batch_stability'],scores['low_rework_rate'],
                         scores['spec_conformance'],avg,get_category(avg),evlr,notes))
                    conn.commit()
                    st.success(f"✅ Tersimpan! Skor: {avg:.1f}")
                    st.rerun()

    with tab3:
        if not df.empty:
            cols_s = ['eval_date','batch_number','quality_uniformity','low_defect_rate',
                      'inter_batch_stability','low_rework_rate','spec_conformance',
                      'average_score','category','evaluator']
            disp = df[cols_s].copy()
            disp.columns = ['Tanggal','Batch','Keseragaman','Defect Rendah',
                            'Stabilitas','Rework Rendah','Kesesuaian Spec','Avg','Kategori','Evaluator']
            st.dataframe(disp, use_container_width=True, hide_index=True)
            if is_admin():
                st.download_button("📥 Export CSV", disp.to_csv(index=False).encode(), "quality_consistency.csv", "text/csv")
        else:
            st.info("Belum ada data.")
    conn.close()
