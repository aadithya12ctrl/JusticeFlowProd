# app.py — JusticeFlow Streamlit entry point
import streamlit as st
import os
import sys

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.theme import inject_css, page_header
from utils.i18n import t, get_lang
from db.database import init_db

# ─── Page Config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="⚖️ JusticeFlow",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Initialize DB ───────────────────────────────────────────────────
init_db()

# ─── Inject CSS ──────────────────────────────────────────────────────
inject_css()

# ─── Sidebar Navigation ──────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding: 1rem 0 1.5rem 0;">
        <h1 style="font-size: 1.8rem; margin:0; letter-spacing: -0.02em;">{t("app_title")}</h1>
        <p style="font-size: 0.8rem; margin: 0.3rem 0 0 0; opacity: 0.8;">{t("app_subtitle")}</p>
    </div>
    """, unsafe_allow_html=True)

    # Hindi toggle
    st.toggle("🇮🇳 हिंदी", key="lang_hindi")

    st.markdown("---")

    page = st.radio(
        "Navigate",
        [
            "🎤 Live Demo",
            "🏠 Home",
            "📝 File Case",
            "📊 DLS Engine",
            "🤝 Negotiation Sandbox",
            "📊 Litigation Risk",
            "🔍 Auto Filter",
            "👨‍⚖️ Judge Cockpit",
            "🕸️ Conflict Graph",
            "📊 Case Analytics",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Seed data button
    if st.button(t("seed_btn"), use_container_width=True):
        from utils.seed_data import seed_all
        cases, entities, edges = seed_all()
        st.success(f"✅ Seeded {cases} cases, {entities} entities, {edges} edges")

    # Show case count
    from db.database import get_all_cases
    all_cases = get_all_cases()
    st.markdown(f"""
    <div style="text-align:center; padding: 1rem 0; opacity: 0.7; font-size: 0.8rem;">
        📁 {len(all_cases)} {t("cases_in_db")}
    </div>
    """, unsafe_allow_html=True)

# ─── Page Routing ─────────────────────────────────────────────────────
if page == "🏠 Home":
    page_header(t("home_title"), t("home_subtitle"))

    # Indian judicial crisis banner
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #2C1A0E, #3D2818); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;">
        <div style="text-align:center; margin-bottom: 1rem;">
            <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.15em; color: #D4A843;">{t("crisis_source")}</span>
        </div>
        <div style="display: flex; justify-content: space-around; text-align: center; flex-wrap: wrap; gap: 1rem;">
            <div>
                <div style="font-size: 2rem; font-weight: 800; color: #C0522B;">4.7 Cr+</div>
                <div style="font-size: 0.8rem; color: #F5F0E8; opacity: 0.8;">{t("cases_pending")}</div>
            </div>
            <div>
                <div style="font-size: 2rem; font-weight: 800; color: #D4A843;">3-5 Yrs</div>
                <div style="font-size: 0.8rem; color: #F5F0E8; opacity: 0.8;">{t("avg_disposal")}</div>
            </div>
            <div>
                <div style="font-size: 2rem; font-weight: 800; color: #6B8F71;">70%</div>
                <div style="font-size: 0.8rem; color: #F5F0E8; opacity: 0.8;">{t("settleable")}</div>
            </div>
            <div>
                <div style="font-size: 2rem; font-weight: 800; color: #F5F0E8;">21</div>
                <div style="font-size: 0.8rem; color: #F5F0E8; opacity: 0.8;">{t("judges_per_million")}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="max-width: 800px;">
        <p style="font-size: 1.1rem; color: #6B4C35; line-height: 1.6;">
            {t("home_desc")}
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{t("feat_dna")}</h3>
            <div style="color: #6B4C35; font-size: 0.9rem;">
                {t("feat_dna_desc")}
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-card">
            <h3>{t("feat_neg")}</h3>
            <div style="color: #6B4C35; font-size: 0.9rem;">
                {t("feat_neg_desc")}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{t("feat_dls")}</h3>
            <div style="color: #6B4C35; font-size: 0.9rem;">
                {t("feat_dls_desc")}
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-card">
            <h3>{t("feat_risk")}</h3>
            <div style="color: #6B4C35; font-size: 0.9rem;">
                {t("feat_risk_desc")}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{t("feat_filter")}</h3>
            <div style="color: #6B4C35; font-size: 0.9rem;">
                {t("feat_filter_desc")}
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-card">
            <h3>{t("feat_graph")}</h3>
            <div style="color: #6B4C35; font-size: 0.9rem;">
                {t("feat_graph_desc")}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick stats
    from db.database import get_connection
    conn = get_connection()
    case_count = conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
    entity_count = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
    hist_count = conn.execute("SELECT COUNT(*) FROM historical_cases").fetchone()[0]
    conn.close()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <h3>{t("active_cases")}</h3>
            <div class="value">{case_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <h3>{t("entities")}</h3>
            <div class="value">{entity_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <h3>{t("historical_cases")}</h3>
            <div class="value">{hist_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <h3>{t("ai_model")}</h3>
            <div class="value" style="font-size: 1rem;">Llama3-70B</div>
        </div>
        """, unsafe_allow_html=True)

elif page == "📝 File Case":
    from pages.page_01_file_case import render
    render()
elif page == "📊 DLS Engine":
    from pages.page_02_dls_engine import render
    render()
elif page == "🤝 Negotiation Sandbox":
    from pages.page_03_negotiation import render
    render()
elif page == "📊 Litigation Risk":
    from pages.page_04_emotion_monitor import render
    render()
elif page == "🔍 Auto Filter":
    from pages.page_05_auto_filter import render
    render()
elif page == "👨‍⚖️ Judge Cockpit":
    from pages.page_06_judge_cockpit import render
    render()
elif page == "🕸️ Conflict Graph":
    from pages.page_07_conflict_graph import render
    render()
elif page == "🎤 Live Demo":
    from pages.page_08_live_demo import render
    render()
elif page == "📊 Case Analytics":
    from pages.page_09_analytics import render
    render()
