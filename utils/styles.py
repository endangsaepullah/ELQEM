import streamlit as st


def apply_global_style():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');

    .stApp { background: #070b14; font-family: 'Inter', sans-serif; color: #e8edf5; }

    [data-testid="stSidebar"] {
        background: #0d1321 !important;
        border-right: 1px solid rgba(0,212,255,0.15);
    }

    h1, h2, h3 {
        font-family: 'Rajdhani', sans-serif !important;
        letter-spacing: 1px;
        color: #e8edf5 !important;
    }

    [data-testid="metric-container"] {
        background: #111827 !important;
        border: 1px solid rgba(0,212,255,0.2) !important;
        border-radius: 10px !important;
        padding: 1rem !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: #0d1321;
        border-radius: 8px;
        border: 1px solid rgba(0,212,255,0.15);
        padding: 4px;
        gap: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #7a9bb5;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 600;
        letter-spacing: 1px;
        border-radius: 6px;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(0,212,255,0.15) !important;
        color: #00d4ff !important;
    }

    .stButton > button {
        background: rgba(0,212,255,0.08);
        border: 1px solid rgba(0,212,255,0.4);
        color: #00d4ff;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 600;
        letter-spacing: 1px;
        border-radius: 6px;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        background: rgba(0,212,255,0.2);
        box-shadow: 0 0 16px rgba(0,212,255,0.2);
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #00d4ff, #0066ff);
        color: #000;
        border: none;
        font-weight: 700;
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background: #0d1321 !important;
        border: 1px solid rgba(0,212,255,0.2) !important;
        color: #e8edf5 !important;
        border-radius: 6px !important;
    }

    hr { border-color: rgba(0,212,255,0.12) !important; }

    .streamlit-expanderHeader {
        background: #111827 !important;
        border: 1px solid rgba(0,212,255,0.15) !important;
        border-radius: 8px !important;
        color: #00d4ff !important;
        font-family: 'Rajdhani', sans-serif !important;
    }

    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #070b14; }
    ::-webkit-scrollbar-thumb { background: #00d4ff44; border-radius: 3px; }
    </style>
    """, unsafe_allow_html=True)


def section_header(title, subtitle=None, icon=""):
    sub = f'<p style="font-size:0.78rem; color:#4a6fa5; margin:0; letter-spacing:2px; text-transform:uppercase;">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
    <div style="margin-bottom:1.5rem; padding-bottom:1rem; border-bottom:1px solid rgba(0,212,255,0.12);">
        <h2 style="font-family:'Rajdhani',sans-serif; font-size:1.8rem; font-weight:700;
                   color:#e8edf5; margin:0; letter-spacing:2px;">{icon} {title.upper()}</h2>
        {sub}
    </div>
    """, unsafe_allow_html=True)


def score_bar(label, value, color="#00d4ff"):
    st.markdown(f"""
    <div style="margin-bottom:0.7rem; padding:0.75rem 1rem;
                background:#111827; border:1px solid {color}22;
                border-left:3px solid {color}; border-radius:8px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:0.8rem; color:#7a9bb5;">{label}</span>
            <span style="font-family:'Rajdhani',sans-serif; font-size:1.15rem;
                         font-weight:700; color:{color};">{value:.1f}</span>
        </div>
        <div style="background:#0d1321; border-radius:4px; height:5px; margin-top:6px; overflow:hidden;">
            <div style="background:{color}; height:100%; width:{value}%;
                        border-radius:4px; opacity:0.8;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def category_banner(score, category):
    colors = {"Sangat Baik": "#00ff88", "Baik": "#00d4ff",
               "Cukup": "#ffd700", "Perlu Perbaikan": "#ff3366"}
    c = colors.get(category, "#7a9bb5")
    st.markdown(f"""
    <div style="padding:0.85rem 1.25rem; background:{c}11; border:1px solid {c}44;
                border-radius:8px; text-align:center;">
        <span style="font-size:0.8rem; color:#7a9bb5;">Kategori: </span>
        <span style="font-family:'Rajdhani',sans-serif; font-size:1.15rem;
                     font-weight:700; color:{c};">{category} ({score:.1f}/100)</span>
    </div>
    """, unsafe_allow_html=True)


def plotly_layout():
    return dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(13,19,33,0.5)',
        font=dict(family='Inter', color='#7a9bb5', size=11),
        xaxis=dict(gridcolor='rgba(0,212,255,0.07)', linecolor='rgba(0,212,255,0.15)'),
        yaxis=dict(gridcolor='rgba(0,212,255,0.07)', linecolor='rgba(0,212,255,0.15)'),
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor='rgba(0,212,255,0.15)', borderwidth=1),
    )
