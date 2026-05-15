import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.database import get_connection
from utils.styles import section_header, plotly_layout
from utils.auth import is_admin
from datetime import date

STAGES = ['Body Assembly','Painting','Join Body + Chassis',
          'Finish Good','Static Test','Dynamic Test','Stockyard']
DTYPES = ['Cacat Las','Cacat Cat','Misfitting','Dimensional Error',
          'Surface Defect','Assembly Error','Leak Test Fail','Rust/Corrosion','Lainnya']
CAUSES = ['Material non-conformance','Operator error','Tooling issue',
          'Process parameter deviation','Design specification unclear','Supplier defect']


def show():
    section_header("Evaluasi Batch Produksi", "Monitoring & Analisis Defect per Batch", "📦")
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Monitoring","➕ Input Batch","🔍 Input Defect","📋 Data Defect"])

    conn = get_connection()
    batch_df  = pd.read_sql("SELECT * FROM batch_production ORDER BY production_date DESC", conn)
    defect_df = pd.read_sql("SELECT * FROM defect_records ORDER BY created_at DESC",        conn)

    with tab1:
        cf1, cf2 = st.columns(2)
        sf = cf1.multiselect("Filter Status", ['All','Completed','In Progress','Planned'], default=['All'])
        sq = cf2.text_input("🔍 Cari Batch")

        fd = batch_df.copy()
        if 'All' not in sf and sf:
            fd = fd[fd['status'].isin(sf)]
        if sq:
            fd = fd[fd['batch_number'].str.contains(sq, case=False)]

        if not fd.empty:
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Total Batch",  len(fd))
            c2.metric("Total Unit",   int(fd['total_units'].sum()))
            c3.metric("Total Defect", int(fd['total_defect'].sum()))
            c4.metric("Avg Defect Rate", f"{fd['defect_rate'].mean():.2f}%")

            st.markdown("---")
            ca, cb = st.columns(2)

            with ca:
                st.markdown("#### 📊 Defect Rate per Batch")
                fdr = fd[::-1]
                fig = go.Figure(go.Bar(
                    x=fdr['batch_number'], y=fdr['defect_rate'],
                    marker=dict(color=['#ff3366' if v>15 else '#ffd700' if v>8 else '#00ff88'
                                       for v in fdr['defect_rate']], opacity=0.85),
                    text=[f"{v:.1f}%" for v in fdr['defect_rate']], textposition='outside'
                ))
                fig.add_hline(y=10, line_dash="dash", line_color="#ffd700",
                              annotation_text="Batas 10%", annotation_font_color="#ffd700")
                lay = plotly_layout()
                lay.update(height=300, xaxis=dict(**lay['xaxis'], tickangle=45, tickfont=dict(size=7)))
                fig.update_layout(**lay)
                st.plotly_chart(fig, use_container_width=True)

            with cb:
                st.markdown("#### 🔄 Rework Rate per Batch")
                fig2 = go.Figure(go.Scatter(
                    x=fdr['batch_number'], y=fdr['rework_rate'],
                    mode='lines+markers', line=dict(color='#ffd700', width=2),
                    marker=dict(size=8), fill='tozeroy', fillcolor='rgba(255,215,0,0.07)'
                ))
                lay2 = plotly_layout()
                lay2.update(height=300, xaxis=dict(**lay2['xaxis'], tickangle=45, tickfont=dict(size=7)))
                fig2.update_layout(**lay2)
                st.plotly_chart(fig2, use_container_width=True)

            # Pareto
            if not defect_df.empty:
                st.markdown("#### 📈 Pareto Chart — Jenis Defect")
                pd_data = defect_df.groupby('defect_type')['quantity'].sum().sort_values(ascending=False)
                cum = pd_data.cumsum() / pd_data.sum() * 100
                fig3 = go.Figure()
                fig3.add_trace(go.Bar(x=pd_data.index, y=pd_data.values, name='Jumlah',
                                       marker=dict(color='#ff3366', opacity=0.8)))
                fig3.add_trace(go.Scatter(x=pd_data.index, y=cum.values, mode='lines+markers',
                                           name='Kumulatif %', line=dict(color='#ffd700', width=2),
                                           marker=dict(size=6), yaxis='y2'))
                fig3.add_hline(y=80, line_dash="dash", line_color="#00ff88", yref='y2',
                               annotation_text="80%", annotation_font_color="#00ff88")
                lay3 = plotly_layout()
                lay3.update(height=300,
                            yaxis2=dict(title='Kumulatif %', overlaying='y', side='right',
                                        range=[0,110], gridcolor='rgba(0,0,0,0)',
                                        tickfont=dict(color='#ffd700')))
                fig3.update_layout(**lay3)
                st.plotly_chart(fig3, use_container_width=True)

            st.markdown("#### 📋 Tabel Batch")
            disp = fd[['batch_number','production_date','total_units','total_defect',
                        'total_rework','defect_rate','rework_rate','pic','status']].copy()
            disp.columns = ['No. Batch','Tanggal','Unit','Defect','Rework','DR(%)','RR(%)','PIC','Status']
            st.dataframe(disp, use_container_width=True, hide_index=True)
            if is_admin():
                st.download_button("📥 Export CSV", disp.to_csv(index=False).encode(), "batch.csv", "text/csv")
        else:
            st.info("Tidak ada data sesuai filter.")

    with tab2:
        if not is_admin():
            st.warning("⛔ Hanya Admin.")
        else:
            cf, ce = st.columns(2)
            with cf:
                st.markdown("#### ➕ Input Batch Baru")
                with st.form("batch_new"):
                    bn  = st.text_input("Nomor Batch*", placeholder="BATCH-KMN-2024-013")
                    pd_ = st.date_input("Tanggal Produksi", value=date.today())
                    c1,c2,c3 = st.columns(3)
                    tu = c1.number_input("Unit",   min_value=0, value=10)
                    td = c2.number_input("Defect", min_value=0, value=0)
                    tr = c3.number_input("Rework", min_value=0, value=0)
                    pc = st.text_input("PIC")
                    st_ = st.selectbox("Status", ['In Progress','Completed','Planned'])
                    nt  = st.text_area("Catatan")
                    if st.form_submit_button("💾 Simpan Batch", use_container_width=True, type="primary"):
                        if bn:
                            dr = round(td/tu*100,2) if tu>0 else 0
                            rr = round(tr/tu*100,2) if tu>0 else 0
                            try:
                                _cur = conn.cursor(); _cur.execute("""INSERT INTO batch_production
                                conn.commit()
                                _cur.close()
                                    (batch_number,production_date,total_units,total_defect,
                                     total_rework,defect_rate,rework_rate,pic,status,notes)
                                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                                    (bn,str(pd_),tu,td,tr,dr,rr,pc,st_,nt))
                                conn.commit()
                                st.success(f"✅ Batch {bn} disimpan!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ {e}")
                        else:
                            st.error("❌ Nomor batch wajib diisi.")

            with ce:
                st.markdown("#### ✏️ Edit / Hapus Batch")
                if not batch_df.empty:
                    sel = st.selectbox("Pilih Batch", batch_df['batch_number'].tolist())
                    row = batch_df[batch_df['batch_number']==sel].iloc[0]
                    with st.form("batch_edit"):
                        tu = st.number_input("Unit",   value=int(row['total_units']))
                        td = st.number_input("Defect", value=int(row['total_defect']))
                        tr = st.number_input("Rework", value=int(row['total_rework']))
                        pc = st.text_input("PIC",    value=str(row['pic'] or ''))
                        st_idx = ['In Progress','Completed','Planned'].index(row['status']) \
                                  if row['status'] in ['In Progress','Completed','Planned'] else 0
                        st_ = st.selectbox("Status", ['In Progress','Completed','Planned'], index=st_idx)
                        nt  = st.text_area("Catatan", value=str(row['notes'] or ''))
                        bu, bd = st.columns(2)
                        upd = bu.form_submit_button("💾 Update",  use_container_width=True, type="primary")
                        dlt = bd.form_submit_button("🗑️ Hapus",   use_container_width=True)
                        if upd:
                            dr = round(td/tu*100,2) if tu>0 else 0
                            rr = round(tr/tu*100,2) if tu>0 else 0
                            _cur = conn.cursor(); _cur.execute("""UPDATE batch_production SET
                            conn.commit()
                            _cur.close()
                                total_units=%s,total_defect=%s,total_rework=%s,
                                defect_rate=%s,rework_rate=%s,pic=%s,status=%s,notes=%s,
                                updated_at=to_char(now(),'YYYY-MM-DD HH24:MI:SS') WHERE batch_number=%s""",
                                (tu,td,tr,dr,rr,pc,st_,nt,sel))
                            conn.commit()
                            st.success("✅ Diupdate!")
                            st.rerun()
                        if dlt:
                            bid = _cur = conn.cursor(); _cur.execute("SELECT id FROM batch_production WHERE batch_number=%s",(sel,)).fetchone()
                            conn.commit()
                            _cur.close()
                            if bid:
                                _cur = conn.cursor(); _cur.execute("DELETE FROM defect_records WHERE batch_id=%s",(bid[0],))
                                conn.commit()
                                _cur.close()
                            _cur = conn.cursor(); _cur.execute("DELETE FROM batch_production WHERE batch_number=%s",(sel,))
                            conn.commit()
                            _cur.close()
                            st.warning(f"🗑️ {sel} dihapus.")
                            st.rerun()

    with tab3:
        if not is_admin():
            st.warning("⛔ Hanya Admin.")
        else:
            if batch_df.empty:
                st.info("Tambahkan batch terlebih dahulu.")
            else:
                with st.form("defect_new"):
                    c1, c2 = st.columns(2)
                    with c1:
                        sb = st.selectbox("Batch*", batch_df['batch_number'].tolist())
                        dt = st.selectbox("Jenis Defect*", DTYPES)
                        ds = st.selectbox("Tahap*", STAGES)
                        qty = st.number_input("Jumlah", min_value=1, value=1)
                        fd_ = st.date_input("Tanggal Ditemukan", value=date.today())
                    with c2:
                        rc  = st.selectbox("Root Cause", CAUSES)
                        ca_ = st.text_area("Corrective Action")
                        pic = st.text_input("PIC")
                        fus = st.selectbox("Status", ['Open','In Progress','Closed'])
                    if st.form_submit_button("💾 Simpan Defect", use_container_width=True, type="primary"):
                        bid_row = batch_df[batch_df['batch_number']==sb].iloc[0]
                        _cur = conn.cursor(); _cur.execute("""INSERT INTO defect_records
                        conn.commit()
                        _cur.close()
                            (batch_id,batch_number,defect_type,defect_stage,quantity,
                             root_cause,corrective_action,pic,follow_up_status,found_date)
                            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                            (int(bid_row['id']),sb,dt,ds,qty,rc,ca_,pic,fus,str(fd_)))
                        conn.commit()
                        st.success(f"✅ Defect disimpan untuk {sb}!")
                        st.rerun()

    with tab4:
        cf1,cf2,cf3 = st.columns(3)
        bf = cf1.selectbox("Filter Batch",  ["Semua"] + (list(batch_df['batch_number']) if not batch_df.empty else []))
        sf = cf2.selectbox("Filter Tahap",  ["Semua"] + STAGES)
        stf = cf3.selectbox("Filter Status",["Semua","Open","In Progress","Closed"])

        fd2 = defect_df.copy()
        if bf  != "Semua": fd2 = fd2[fd2['batch_number']     == bf]
        if sf  != "Semua": fd2 = fd2[fd2['defect_stage']     == sf]
        if stf != "Semua": fd2 = fd2[fd2['follow_up_status'] == stf]

        if not fd2.empty:
            cols_s = ['batch_number','defect_type','defect_stage','quantity',
                      'root_cause','corrective_action','pic','follow_up_status','found_date']
            disp2 = fd2[cols_s].copy()
            disp2.columns = ['Batch','Jenis Defect','Tahap','Qty',
                             'Root Cause','Corrective Action','PIC','Status','Tanggal']
            st.dataframe(disp2, use_container_width=True, hide_index=True)
            if is_admin():
                st.download_button("📥 Export CSV", disp2.to_csv(index=False).encode(), "defects.csv", "text/csv")
        else:
            st.info("Tidak ada data sesuai filter.")
    conn.close()
