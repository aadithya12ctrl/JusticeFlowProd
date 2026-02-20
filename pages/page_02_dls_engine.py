# pages/page_02_dls_engine.py — Dismissal Likelihood Score gauge + breakdown
import streamlit as st
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.theme import page_header
from utils.charts import render_gauge, render_reason_bars
from config import get_llm
from db.database import get_all_cases, get_case, update_case
from agents.dls_agent import compute_dls


def render():
    page_header("DLS Engine", "AI Dismissal Probability Analysis")

    cases = get_all_cases()
    if not cases:
        st.info("📭 No cases found. File a case first from the '📝 File Case' page.")
        return

    # Case selector
    case_options = {f"#{c['id']} — {c['title']}": c['id'] for c in cases}
    selected_label = st.selectbox("Select a case to analyze", list(case_options.keys()))
    case_id = case_options[selected_label]
    case = get_case(case_id)

    if not case:
        st.error("Case not found.")
        return

    # Check for existing DLS score
    existing_dls = case.get("dls_score")
    existing_reasons = case.get("dls_reasons")

    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        run_analysis = st.button("🔍 Run DLS Analysis", use_container_width=True)
    with col_info:
        if existing_dls is not None:
            st.markdown(f"""
            <div style="padding:0.5rem; color:#6B4C35; font-size:0.85rem;">
                ℹ️ Previous score: {existing_dls:.0f}/100. Click to re-analyze.
            </div>
            """, unsafe_allow_html=True)

    if run_analysis:
        with st.spinner("🔍 Analyzing dismissal probability..."):
            try:
                llm = get_llm()
                result = compute_dls(case, llm)
            except Exception as e:
                st.error(f"⚠️ Analysis failed: {str(e)[:100]}")
                return

            # Save to DB
            update_case(
                case_id,
                dls_score=result["dls"],
                dls_reasons=json.dumps(result["reasons"]),
                status="scored",
            )

        # Reload case
        case = get_case(case_id)
        existing_dls = result["dls"]
        existing_reasons = json.dumps(result["reasons"])
        explanation = result["explanation"]
    else:
        explanation = ""

    if existing_dls is not None:
        dls = float(existing_dls)
        try:
            reasons = json.loads(existing_reasons) if isinstance(existing_reasons, str) else existing_reasons or {}
        except (json.JSONDecodeError, TypeError):
            reasons = {}

        # Warning banner for high DLS
        if dls > 75:
            st.markdown(f"""
            <div class="warning-banner">
                ⚠️ HIGH DISMISSAL RISK: {dls:.0f}% — This case has a high probability of being dismissed.
                Review the breakdown below carefully before proceeding.
            </div>
            """, unsafe_allow_html=True)
            if st.button("⚡ Proceed Anyway", key="proceed"):
                st.success("✅ Override accepted. Case will proceed despite high DLS score.")

        st.markdown("<br>", unsafe_allow_html=True)

        # Main layout
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### 📊 Dismissal Probability")
            fig = render_gauge(dls, "DLS Score")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### 📋 Reason Breakdown")
            if reasons:
                bars_html = render_reason_bars(reasons)
                st.markdown(bars_html, unsafe_allow_html=True)
            else:
                st.info("No detailed breakdown available.")

        # Explanation
        if explanation:
            st.markdown("### 💡 AI Explanation")
            st.markdown(f"""
            <div class="metric-card">
                <p style="color:#2C1A0E; font-size:1rem; line-height:1.6; margin:0;">{explanation}</p>
            </div>
            """, unsafe_allow_html=True)

        # Case summary
        with st.expander("📋 Case Details"):
            st.markdown(f"**Title:** {case['title']}")
            st.markdown(f"**Category:** {case.get('category', 'N/A').replace('_',' ').title()}")
            st.markdown(f"**Jurisdiction:** {case.get('jurisdiction', 'N/A')}")
            st.markdown(f"**Claim Amount:** ${case.get('claim_amount', 0):,.2f}")
            st.markdown(f"**Description:** {case['description']}")
    else:
        st.markdown("""
        <div class="metric-card" style="text-align:center;">
            <p style="color:#6B4C35; margin:0;">Click "🔍 Run DLS Analysis" to compute the dismissal probability score.</p>
        </div>
        """, unsafe_allow_html=True)
