import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.database import get_connection, fetchall, fetchone, get_category
from utils.styles import section_header, plotly_layout


def show():
    section_header("Dashboard Utama", "Integrated Engineering Quality Lifecycle Evaluation Platform", "🏠")

    conn = get_connection()
    batch_df = pd.DataFrame(fetchall(conn, "SELECT * FROM batch_production ORDER BY production_date"))
    defect_df = pd.DataFrame(fetchall(conn, "SELECT * FROM defect_records"))

    total_batch  = len(batch_df)
    total_units  = int(batch_df['total_units'].sum())  if not batch_df.empty else 0
    total_defect = int(batch_df['total_defect'].sum()) if not batch_df.empty else 0
    total_rework = int(batch_df['total_rework'].sum()) if not batch_df.empty else 0
    avg_dr = round(batch_df['defect_rate'].mean(),  2) if not batch_df.empty else 0
    avg_rr = round(batch_df['rework_rate'].mean(),  2) if not batch_df.empty else 0

    iso_s  = pd.DataFrame(fetchall(conn, "SELECT average_score FROM iso9001_evaluation      ORDER BY eval_date DESC LIMIT 1"))
    iatf_s = pd.DataFrame(fetchall(conn, "SELECT average_score FROM iatf16949_evaluation     ORDER BY eval_date DESC LIMIT 1"))
    lc_s   = pd.DataFrame(fetchall(conn, "SELECT average_score FROM engineering_lifecycle    ORDER BY eval_date DESC LIMIT 1"))
    qc_s   = pd.DataFrame(fetchall(conn, "SELECT average_score FROM quality_consistency      ORDER BY eval_date DESC LIMIT 1"))
    conn.close()

    iso  = float(iso_s.iloc[0]['average_score'])  if not iso_s.empty  else 0
    iatf = float(iatf_s.iloc[0]['average_score']) if not iatf_s.empty else 0
    lc   = float(lc_s.iloc[0]['average_score'])   if not lc_s.empty   else 0
    qc   = float(qc_s.iloc[0]['average_score'])   if not qc_s.empty   else 0
    iqls = round(iso*0.25 + iatf*0.20 + lc*0.35 + qc*0.20, 1)

    # ── KPI row ─────────────────────────────────────────────
    st.markdown("#### 📊 Key Performance Indicators")
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Total Batch",    total_batch)
    c2.metric("Total Unit",     total_units)
    c3.metric("Total Defect",   total_defect)
    c4.metric("Defect Rate",    f"{avg_dr}%")
    c5.metric("Rework Rate",    f"{avg_rr}%")
    c6.metric("IQLS Score",     iqls)

    st.markdown("---")

    # ── Score bars + Trend ───────────────────────────────────
    col_l, col_r = st.columns([1, 2])

    with col_l:
        st.markdown("#### 🏆 Skor Evaluasi Terkini")
        from utils.styles import score_bar
        score_bar("📊 ISO 9001 (X1)",              iso,  "#00d4ff")
        score_bar("🏭 IATF 16949 (X2)",             iatf, "#0066ff")
        score_bar("⚙️ Eng. Lifecycle (X3) ⭐",      lc,   "#00ff88")
        score_bar("✅ Konsistensi Mutu (Y)",          qc,   "#ffd700")

        cat = get_category(iqls)
        colors = {"Sangat Baik":"#00ff88","Baik":"#00d4ff","Cukup":"#ffd700","Perlu Perbaikan":"#ff3366"}
        c = colors.get(cat,"#7a9bb5")
        st.markdown(f"""
        <div style="margin-top:1rem; padding:1rem; text-align:center;
                    background:{c}11; border:2px solid {c}44; border-radius:10px;">
            <div style="font-size:0.65rem; color:#7a9bb5; letter-spacing:2px; text-transform:uppercase;">
                INTEGRATED QUALITY LIFECYCLE SCORE
            </div>
            <div style="font-family:'Rajdhani',sans-serif; font-size:3.2rem;
                        font-weight:700; color:{c}; line-height:1.1;">{iqls}</div>
            <div style="font-family:'Rajdhani',sans-serif; font-size:1rem;
                        font-weight:600; color:{c};">{cat}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_r:
        st.markdown("#### 📈 Trend Defect & Rework per Batch")
        if not batch_df.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=batch_df['batch_number'], y=batch_df['defect_rate'],
                mode='lines+markers', name='Defect Rate (%)',
                line=dict(color='#ff3366', width=2),
                fill='tozeroy', fillcolor='rgba(255,51,102,0.08)'
            ))
            fig.add_trace(go.Scatter(
                x=batch_df['batch_number'], y=batch_df['rework_rate'],
                mode='lines+markers', name='Rework Rate (%)',
                line=dict(color='#ffd700', width=2)
            ))
            lay = plotly_layout()
            lay.update(height=270, xaxis=dict(**lay['xaxis'], tickangle=45, tickfont=dict(size=8)))
            fig.update_layout(**lay)
            st.plotly_chart(fig, use_container_width=True)

        if not batch_df.empty:
            sc = batch_df['status'].value_counts()
            fig2 = go.Figure(go.Bar(
                x=sc.values, y=sc.index, orientation='h',
                marker=dict(color=['#00ff88' if s=='Completed' else '#ffd700' if s=='In Progress' else '#00d4ff'
                                   for s in sc.index], opacity=0.8)
            ))
            lay2 = plotly_layout()
            lay2.update(height=160, margin=dict(l=90,r=20,t=30,b=10))
            fig2.update_layout(**lay2)
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 🔍 Defect per Tahap Produksi")
        if not defect_df.empty:
            sc2 = defect_df.groupby('defect_stage')['quantity'].sum().sort_values()
            fig3 = go.Figure(go.Bar(
                x=sc2.values, y=sc2.index, orientation='h',
                marker=dict(color='#0066ff', opacity=0.8)
            ))
            lay3 = plotly_layout()
            lay3.update(height=300, margin=dict(l=130,r=20,t=30,b=20))
            fig3.update_layout(**lay3)
            st.plotly_chart(fig3, use_container_width=True)

    with col_b:
        st.markdown("#### 🏆 Top Jenis Defect")
        if not defect_df.empty:
            td = defect_df.groupby('defect_type')['quantity'].sum().sort_values(ascending=False).head(7)
            fig4 = go.Figure(go.Pie(
                labels=td.index, values=td.values, hole=0.5,
                marker=dict(colors=['#ff3366','#ff6b35','#ffd700','#00d4ff',
                                    '#0066ff','#00ff88','#a78bfa']),
                textfont=dict(size=10)
            ))
            lay4 = plotly_layout()
            lay4.update(height=300)
            fig4.update_layout(**lay4)
            st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 📋 Batch Terkini")
    if not batch_df.empty:
        show_df = batch_df[['batch_number','production_date','total_units',
                             'total_defect','defect_rate','rework_rate','status']].tail(8).copy()
        show_df.columns = ['No. Batch','Tanggal','Unit','Defect','Defect Rate(%)','Rework Rate(%)','Status']
        st.dataframe(show_df, use_container_width=True, hide_index=True)
