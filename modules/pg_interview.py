import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.database import get_connection, fetchall, fetchone
from utils.styles import section_header, plotly_layout
from utils.auth import is_admin
from datetime import date

CATS = ['ISO 9001','IATF 16949','Engineering Lifecycle','Konsistensi Mutu',
        'Manajemen Produksi','SDM','Supplier Quality','Lainnya']


def show():
    section_header("Data Wawancara", "Pendalaman Kualitatif Penelitian Tesis", "💬")
    tab1, tab2, tab3 = st.tabs(["📋 Daftar Wawancara","➕ Input Wawancara","📊 Summary Insight"])

    conn = get_connection()
    df = pd.DataFrame(fetchall(conn, "SELECT * FROM interview_data ORDER BY interview_date DESC"))

    with tab1:
        if df.empty:
            st.info("Belum ada data wawancara.")
        else:
            c1,c2,c3 = st.columns(3)
            c1.metric("Total Narasumber", len(df))
            c2.metric("Unit Kerja",       df['work_unit'].nunique())
            c3.metric("Kategori Temuan",  df['finding_category'].nunique())

            cf = st.multiselect("Filter Kategori", ["Semua"]+CATS, default=["Semua"])
            fdf = df if "Semua" in cf or not cf else df[df['finding_category'].isin(cf)]

            for _, row in fdf.iterrows():
                with st.expander(f"🎤 {row['informant_name']} — {row['position']} | {row['interview_date']}"):
                    c1, c2 = st.columns(2)
                    c1.markdown(f"**Unit Kerja:** {row['work_unit']}")
                    c1.markdown(f"**Kategori:** `{row['finding_category']}`")
                    c2.markdown(f"**Tanggal:** {row['interview_date']}")
                    c2.markdown(f"**Pewawancara:** {row.get('interviewer','-')}")
                    st.markdown("**Hasil Wawancara:**")
                    st.markdown(f"""
                    <div style="padding:.85rem 1rem; background:#111827;
                                border-left:3px solid #00d4ff; border-radius:0 8px 8px 0;
                                color:#e8edf5; font-size:.85rem; line-height:1.6; margin-bottom:.5rem;">
                        {row['interview_result'] or '-'}
                    </div>
                    """, unsafe_allow_html=True)
                    if row.get('key_insights'):
                        st.markdown(f"""
                        <div style="padding:.65rem 1rem; background:rgba(255,215,0,.08);
                                    border-left:3px solid #ffd700; border-radius:0 6px 6px 0;
                                    color:#ffd700; font-size:.85rem;">
                            💡 {row['key_insights']}
                        </div>
                        """, unsafe_allow_html=True)
                    if is_admin():
                        if st.button("🗑️ Hapus", key=f"del_iv_{row['id']}"):
                            conn.execute("DELETE FROM interview_data WHERE id=?", (row['id'],))
                            conn.commit()
                            st.rerun()

            if is_admin():
                st.download_button("📥 Export CSV", fdf.to_csv(index=False).encode(), "wawancara.csv", "text/csv")

    with tab2:
        if not is_admin():
            st.warning("⛔ Hanya Admin.")
        else:
            with st.form("iv_form"):
                c1, c2 = st.columns(2)
                with c1:
                    iv_date = st.date_input("Tanggal Wawancara", value=date.today())
                    name    = st.text_input("Nama Narasumber*")
                    pos     = st.text_input("Jabatan*")
                with c2:
                    unit    = st.text_input("Unit Kerja*")
                    fcat    = st.selectbox("Kategori Temuan", CATS)
                    ivr     = st.text_input("Pewawancara")
                result   = st.text_area("Hasil Wawancara*", height=180)
                insights = st.text_area("Key Insights / Highlight", height=80)
                if st.form_submit_button("💾 Simpan", use_container_width=True, type="primary"):
                    if name and result:
                        conn.execute("""INSERT INTO interview_data
                        conn.commit()
                            (interview_date,informant_name,position,work_unit,
                             interview_result,key_insights,finding_category,interviewer)
                            VALUES(?,?,?,?,?,?,?,?)""",
                            (str(iv_date),name,pos,unit,result,insights,fcat,ivr))
                        conn.commit()
                        st.success(f"✅ Data wawancara {name} tersimpan!")
                        st.rerun()
                    else:
                        st.error("❌ Nama dan hasil wawancara wajib diisi.")

    with tab3:
        if not df.empty:
            sc = df['finding_category'].value_counts()
            fig = go.Figure(go.Bar(
                x=sc.values, y=sc.index, orientation='h',
                marker=dict(color=['#00d4ff','#0066ff','#00ff88','#ffd700',
                                   '#ff6b35','#ff3366','#a78bfa','#7a9bb5'][:len(sc)], opacity=0.85)
            ))
            lay = plotly_layout()
            lay.update(height=280, title='Distribusi Temuan per Kategori',
                       margin=dict(l=140,r=20,t=50,b=20))
            fig.update_layout(**lay)
            st.plotly_chart(fig, use_container_width=True)

            for cat in df['finding_category'].unique():
                insights = df[df['finding_category']==cat]['key_insights'].dropna().tolist()
                if insights:
                    with st.expander(f"💡 {cat} ({len(df[df['finding_category']==cat])} narasumber)"):
                        for i, ins in enumerate(insights, 1):
                            st.markdown(f"**{i}.** {ins}")
        else:
            st.info("Belum ada data.")
    conn.close()
