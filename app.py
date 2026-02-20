# app.py — JusticeFlow Streamlit entry point
import streamlit as st
import os
import sys

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.theme import inject_css, page_header
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
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 1.5rem 0;">
        <h1 style="font-size: 1.8rem; margin:0; letter-spacing: -0.02em;">⚖️ JusticeFlow</h1>
        <p style="font-size: 0.8rem; margin: 0.3rem 0 0 0; opacity: 0.8;">AI-Powered Dispute Resolution</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio(
        "Navigate",
        [
            "🏠 Home",
            "📝 File Case",
            "📊 DLS Engine",
            "🤝 Negotiation Sandbox",
            "💭 Emotion Monitor",
            "🔍 Auto Filter",
            "👨‍⚖️ Judge Cockpit",
            "🕸️ Conflict Graph",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Seed data button
    if st.button("🌱 Seed Demo Data", use_container_width=True):
        from utils.seed_data import seed_all
        cases, entities, edges = seed_all()
        st.success(f"✅ Seeded {cases} cases, {entities} entities, {edges} edges")

    # Show case count
    from db.database import get_all_cases
    all_cases = get_all_cases()
    st.markdown(f"""
    <div style="text-align:center; padding: 1rem 0; opacity: 0.7; font-size: 0.8rem;">
        📁 {len(all_cases)} cases in database
    </div>
    """, unsafe_allow_html=True)

# ─── Page Routing ─────────────────────────────────────────────────────
if page == "🏠 Home":
    page_header("JusticeFlow", "AI-Powered Dispute Resolution Platform")

    st.markdown("""
    <div style="max-width: 800px;">
        <p style="font-size: 1.1rem; color: #6B4C35; line-height: 1.6;">
            Transform dispute resolution from a slow, paper-bound process into an intelligent, 
            real-time system that saves courts time, guides parties toward fair settlements, 
            and exposes bad actors through relational graph intelligence.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🧬 Case DNA</h3>
            <div style="color: #6B4C35; font-size: 0.9rem;">
                AI fingerprinting matches cases to historical twins using 6D vector similarity.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="metric-card">
            <h3>🤝 Negotiation AI</h3>
            <div style="color: #6B4C35; font-size: 0.9rem;">
                Multi-agent system mediates autonomously between plaintiff and defendant.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 DLS Engine</h3>
            <div style="color: #6B4C35; font-size: 0.9rem;">
                Predicts dismissal probability with per-reason breakdown and smart warnings.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="metric-card">
            <h3>💭 Emotion Layer</h3>
            <div style="color: #6B4C35; font-size: 0.9rem;">
                Real-time emotional temperature monitoring with cooling-off alerts.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🔍 Auto Filter</h3>
            <div style="color: #6B4C35; font-size: 0.9rem;">
                Rule-based + LLM hybrid filter catches jurisdiction issues and trivial claims.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="metric-card">
            <h3>🕸️ Conflict Graph</h3>
            <div style="color: #6B4C35; font-size: 0.9rem;">
                NetworkX-powered graph reveals repeat offenders and systemic abuse patterns.
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
            <h3>Active Cases</h3>
            <div class="value">{case_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <h3>Entities</h3>
            <div class="value">{entity_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <h3>Historical Cases</h3>
            <div class="value">{hist_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <h3>AI Model</h3>
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
elif page == "💭 Emotion Monitor":
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
