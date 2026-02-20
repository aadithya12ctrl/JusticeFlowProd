# utils/theme.py — CSS injection with terracotta design language
import streamlit as st


def inject_css():
    """Inject the JusticeFlow terracotta/cream/brown design system CSS."""
    st.markdown("""
    <style>
    /* ─── Import Fonts ─────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ─── Root Variables ───────────────────────────────────────── */
    :root {
        --primary: #C0522B;
        --primary-hover: #A0422B;
        --secondary: #8B5E3C;
        --bg: #F5F0E8;
        --surface: #EDE3D4;
        --accent: #A0522D;
        --text-dark: #2C1A0E;
        --text-light: #6B4C35;
        --success: #6B8F71;
        --warning: #D4A843;
        --danger: #B03A2E;
    }

    /* ─── Base App ─────────────────────────────────────────────── */
    .stApp {
        background-color: var(--bg) !important;
        font-family: 'Inter', sans-serif !important;
        color: var(--text-dark) !important;
    }
    /* Force all main content text to dark */
    .stApp p, .stApp span, .stApp li, .stApp div, .stApp label {
        color: var(--text-dark) !important;
    }

    /* ─── Sidebar ──────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #8B5E3C 0%, #6B4C35 100%) !important;
        border-right: 3px solid var(--primary) !important;
    }
    /* Sidebar text stays cream/light */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] li {
        color: #F5F0E8 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-weight: 500 !important;
        padding: 0.3rem 0 !important;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        color: var(--warning) !important;
    }
    /* Hide Streamlit auto-detected multipage links at top of sidebar */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    section[data-testid="stSidebar"] > div > div > div > div > ul {
        display: none !important;
    }

    /* ─── Headers ──────────────────────────────────────────────── */
    h1, h2, h3 {
        color: var(--text-dark) !important;
        font-family: 'Inter', sans-serif !important;
    }
    h1 {
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
    }

    /* ─── Buttons ──────────────────────────────────────────────── */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(192, 82, 43, 0.25) !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--primary-hover) 0%, #8B4513 100%) !important;
        box-shadow: 0 4px 16px rgba(192, 82, 43, 0.4) !important;
        transform: translateY(-1px) !important;
    }

    /* ─── Inputs ───────────────────────────────────────────────── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background: var(--surface) !important;
        border: 1px solid #C0522B33 !important;
        border-radius: 8px !important;
        color: var(--text-dark) !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 2px rgba(192, 82, 43, 0.15) !important;
    }

    /* ─── Metric Cards ─────────────────────────────────────────── */
    .metric-card {
        background: var(--surface);
        border-left: 4px solid var(--primary);
        border-radius: 10px;
        padding: 1.2rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(44, 26, 14, 0.08);
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(44, 26, 14, 0.12);
    }
    .metric-card h3 {
        margin: 0 0 0.5rem 0;
        font-size: 0.85rem;
        color: var(--text-light);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-card .value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-dark);
    }

    /* ─── Warning Banner ───────────────────────────────────────── */
    .warning-banner {
        background: linear-gradient(135deg, #C0522B, #B03A2E);
        color: white;
        padding: 1.2rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(192, 82, 43, 0.3);
        animation: pulse-border 2s infinite;
    }
    @keyframes pulse-border {
        0%, 100% { box-shadow: 0 4px 12px rgba(192, 82, 43, 0.3); }
        50% { box-shadow: 0 4px 20px rgba(192, 82, 43, 0.6); }
    }

    /* ─── Success Card ─────────────────────────────────────────── */
    .success-card {
        background: linear-gradient(135deg, #6B8F71, #5A7D60);
        color: white;
        padding: 1.2rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(107, 143, 113, 0.3);
    }

    /* ─── Case Card ────────────────────────────────────────────── */
    .case-card {
        background: white;
        border: 2px solid var(--primary);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(44, 26, 14, 0.08);
    }
    .case-card .case-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text-dark);
        margin-bottom: 0.5rem;
    }
    .case-card .case-meta {
        font-size: 0.85rem;
        color: var(--text-light);
    }

    /* ─── Chat Bubbles ─────────────────────────────────────────── */
    .chat-plaintiff {
        background: #A0522D22;
        border-left: 3px solid var(--accent);
        border-radius: 0 12px 12px 0;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .chat-defendant {
        background: #8B5E3C22;
        border-right: 3px solid var(--secondary);
        border-radius: 12px 0 0 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }

    /* ─── Progress Bar ─────────────────────────────────────────── */
    .filter-step {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.6rem 1rem;
        margin: 0.3rem 0;
        border-radius: 8px;
        background: var(--surface);
        transition: all 0.3s ease;
    }
    .filter-step.pass { border-left: 4px solid var(--success); }
    .filter-step.fail { border-left: 4px solid var(--danger); }
    .filter-step.pending { border-left: 4px solid var(--warning); }

    /* ─── Dark Judge Card ──────────────────────────────────────── */
    .judge-card {
        background: linear-gradient(135deg, #2C1A0E, #3D2818);
        color: #F5F0E8;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }
    .judge-card h4 {
        color: var(--warning) !important;
        margin: 0 0 0.5rem 0;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    .judge-card .value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #F5F0E8;
    }

    /* ─── Streamlit Overrides ──────────────────────────────────── */
    .stProgress > div > div > div > div {
        background-color: var(--primary) !important;
    }
    div[data-testid="stExpander"] {
        background: var(--surface) !important;
        border-radius: 10px !important;
        border: 1px solid #C0522B22 !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: var(--surface) !important;
        border-radius: 8px 8px 0 0 !important;
        color: var(--text-dark) !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--primary) !important;
        color: white !important;
    }

    /* ─── Scrollbar ────────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb {
        background: var(--secondary);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover { background: var(--primary); }

    /* ─── Explicit overrides for dark-background containers ──── */
    .warning-banner, .warning-banner * { color: white !important; }
    .success-card, .success-card * { color: white !important; }
    .judge-card, .judge-card p, .judge-card span, .judge-card div { color: #F5F0E8 !important; }
    .judge-card h4 { color: var(--warning) !important; }
    .judge-card .value { color: #F5F0E8 !important; }
    .stButton > button, .stButton > button span { color: white !important; }
    .stTabs [aria-selected="true"] { color: white !important; }

    /* Any inline dark gradient box — force cream text inside */
    [style*="background:linear-gradient"] p,
    [style*="background:linear-gradient"] span,
    [style*="background:linear-gradient"] div,
    [style*="background: linear-gradient"] p,
    [style*="background: linear-gradient"] span,
    [style*="background: linear-gradient"] div,
    [style*="background:#2C1A0E"] p,
    [style*="background:#2C1A0E"] span,
    [style*="background:#2C1A0E"] div,
    [style*="background:#3D2818"] p,
    [style*="background:#3D2818"] span,
    [style*="background:#3D2818"] div {
        color: #F5F0E8 !important;
    }

    /* ─── Code blocks (st.code) ─── */
    .stCode, .stCode pre, .stCode code, .stCode span,
    [data-testid="stCode"] pre, [data-testid="stCode"] code, [data-testid="stCode"] span {
        color: #F5F0E8 !important;
    }
    </style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    """Render a styled page header."""
    st.markdown(f"""
    <div style="padding: 1rem 0 1.5rem 0;">
        <h1 style="margin:0; font-size:2rem;">⚖️ {title}</h1>
        {"<p style='color: #6B4C35; margin: 0.3rem 0 0 0; font-size: 1rem;'>" + subtitle + "</p>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)


def metric_card(title: str, value: str, color: str = "#C0522B"):
    """Render a styled metric card."""
    return f"""
    <div class="metric-card" style="border-left-color: {color};">
        <h3>{title}</h3>
        <div class="value" style="color: {color};">{value}</div>
    </div>
    """
