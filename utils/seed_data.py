"""
seed_data.py — isi data dummy hanya jika tabel batch masih kosong.
Aman dipanggil berulang kali (idempotent).
"""
import random
from datetime import datetime, timedelta
from utils.database import get_connection, get_category, get_lifecycle_maturity
from utils.auth import hash_password


def seed_dummy_data():
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) AS cnt FROM batch_production")
    if c.fetchone()['cnt'] > 0:
        c.close(); conn.close()
        return

    # Extra users
    for u in [
        ('viewer1',    hash_password('viewer123'),    'Budi Santoso', 'viewer', 'budi@pindad.com'),
        ('qc_manager', hash_password('qcmanager123'), 'Siti Rahma',   'admin',  'siti@pindad.com'),
    ]:
        try:
            c.execute(
                "INSERT INTO users (username,password_hash,full_name,role,email)"
                " VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING", u)
        except Exception:
            pass

    base   = datetime(2024, 1, 15)
    stages = ['Body Assembly','Painting','Join Body + Chassis',
              'Finish Good','Static Test','Dynamic Test','Stockyard']
    dtypes = ['Cacat Las','Cacat Cat','Misfitting','Dimensional Error',
              'Surface Defect','Assembly Error','Leak Test Fail']
    pics   = ['Andi Wijaya','Rahmat Hidayat','Deni Kusuma']

    for i in range(1, 13):
        d      = base + timedelta(days=i * 25)
        units  = random.randint(8, 15)
        defects= random.randint(1, max(1, units // 3))
        reworks= random.randint(0, defects)
        status = 'Completed' if i < 10 else ('In Progress' if i == 10 else 'Planned')

        c.execute("""INSERT INTO batch_production
            (batch_number,production_date,total_units,total_defect,total_rework,
             defect_rate,rework_rate,pic,status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
            (f"BATCH-KMN-2024-{i:03d}", d.strftime('%Y-%m-%d'),
             units, defects, reworks,
             round(defects/units*100, 2), round(reworks/units*100, 2),
             random.choice(pics), status))

        bid = c.fetchone()['id']
        for _ in range(defects):
            c.execute("""INSERT INTO defect_records
                (batch_id,batch_number,defect_type,defect_stage,quantity,
                 root_cause,corrective_action,pic,follow_up_status,found_date)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (bid, f"BATCH-KMN-2024-{i:03d}",
                 random.choice(dtypes), random.choice(stages),
                 random.randint(1,3),
                 random.choice(['Material non-conformance','Operator error',
                                'Tooling issue','Process parameter deviation']),
                 random.choice(['Rework','Replace','Training operator','Process re-evaluation']),
                 random.choice(['Andi','Rahmat','Siti','Deni']),
                 random.choice(['Closed','Open','In Progress']),
                 d.strftime('%Y-%m-%d')))

    # ISO 9001
    for i in range(6):
        ed = (base + timedelta(days=i*50)).strftime('%Y-%m-%d')
        s  = [round(random.uniform(65,90),1) for _ in range(5)]
        avg= round(sum(s)/5, 2)
        c.execute("""INSERT INTO iso9001_evaluation
            (eval_date,batch_number,process_documentation,process_control,
             internal_audit,corrective_action,continuous_improvement,
             average_score,category,evaluator)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (ed,f"BATCH-KMN-2024-{i+1:03d}",
             s[0],s[1],s[2],s[3],s[4],avg,get_category(avg),'Siti Rahma'))

    # IATF 16949
    for i in range(6):
        ed = (base + timedelta(days=i*50)).strftime('%Y-%m-%d')
        s  = [round(random.uniform(62,89),1) for _ in range(4)]
        avg= round(sum(s)/4, 2)
        c.execute("""INSERT INTO iatf16949_evaluation
            (eval_date,batch_number,risk_based_thinking,defect_prevention,
             supplier_quality,continuous_improvement,average_score,category,evaluator)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (ed,f"BATCH-KMN-2024-{i+1:03d}",
             s[0],s[1],s[2],s[3],avg,get_category(avg),'Siti Rahma'))

    # Engineering Lifecycle
    for i in range(6):
        ed = (base + timedelta(days=i*50)).strftime('%Y-%m-%d')
        s  = [round(random.uniform(58,92),1) for _ in range(6)]
        avg= round(sum(s)/6, 2)
        c.execute("""INSERT INTO engineering_lifecycle
            (eval_date,batch_number,design_control,change_control,
             verification_validation,integration_process,traceability,
             design_change_communication,average_score,maturity_level,evaluator)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (ed,f"BATCH-KMN-2024-{i+1:03d}",
             s[0],s[1],s[2],s[3],s[4],s[5],
             avg,get_lifecycle_maturity(avg),'Andi Wijaya'))

    # Quality Consistency
    for i in range(6):
        ed = (base + timedelta(days=i*50)).strftime('%Y-%m-%d')
        s  = [round(random.uniform(65,91),1) for _ in range(5)]
        avg= round(sum(s)/5, 2)
        c.execute("""INSERT INTO quality_consistency
            (eval_date,batch_number,quality_uniformity,low_defect_rate,
             inter_batch_stability,low_rework_rate,spec_conformance,
             average_score,category,evaluator)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (ed,f"BATCH-KMN-2024-{i+1:03d}",
             s[0],s[1],s[2],s[3],s[4],avg,get_category(avg),'Rahmat Hidayat'))

    # Interview
    for row in [
        ('2024-03-10','Ir. Bambang Suryadi','Kepala Divisi Produksi','Divisi Manufaktur',
         'Engineering lifecycle menjadi faktor kritis. Perubahan desain yang tidak terkontrol menjadi sumber utama defect.',
         'Change control perlu diperkuat','Engineering Lifecycle','Peneliti'),
        ('2024-03-15','Dr. Retno Wulandari','Manajer QA','Quality Assurance',
         'Implementasi IATF 16949 sudah berjalan namun supplier quality masih menjadi tantangan.',
         'Supplier qualification perlu ditingkatkan','IATF 16949','Peneliti'),
        ('2024-04-01','Agus Prasetyo, M.T.','Engineer Senior','R&D Engineering',
         'Dokumentasi ISO 9001 sudah baik namun gap antara dokumen dan praktik lapangan masih ada.',
         'Perlu bridging antara dokumen dan lapangan','ISO 9001','Peneliti'),
    ]:
        c.execute("""INSERT INTO interview_data
            (interview_date,informant_name,position,work_unit,
             interview_result,key_insights,finding_category,interviewer)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""", row)

    conn.commit()
    c.close()
    conn.close()
