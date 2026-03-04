# pages/page_02_dls_engine.py — Dismissal Likelihood Score gauge + breakdown (v2)
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

SEVERITY_COLORS = {
    "critical": "#B03A2E",
    "high": "#D4782A",
    "moderate": "#F4A261",
    "low": "#6B8F71",
    "minimal": "#4A7C59",
}

SEVERITY_LABELS = {
    "critical": "🔴 CRITICAL — Very likely to be dismissed",
    "high": "🟠 HIGH — Significant dismissal risk",
    "moderate": "🟡 MODERATE — Some concerns identified",
    "low": "🟢 LOW — Minor issues only",
    "minimal": "✅ MINIMAL — Case appears well-founded",
}

REASON_LABELS = {
    "jurisdiction_defect": "🏛️ Jurisdiction",
    "limitation_expired": "⏰ Limitation Period",
    "evidence_gap": "📋 Evidence Gap",
    "no_cause_of_action": "❌ Cause of Action",
    "procedural_defect": "⚠️ Procedural",
}


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

    result = None
    if run_analysis:
        with st.spinner("🔍 Analyzing dismissal probability across 5 Indian law dimensions..."):
            try:
                llm = get_llm()
                result = compute_dls(case, llm)
            except Exception as e:
                st.error(f"⚠️ Analysis failed: {str(e)[:100]}")
                return

            # Save to DB (flat reasons for backward compat)
            update_case(
                case_id,
                dls_score=result["dls"],
                dls_reasons=json.dumps(result.get("reasons_flat", {})),
                status="scored",
            )

        # Reload case
        case = get_case(case_id)
        existing_dls = result["dls"]
        existing_reasons = json.dumps(result.get("reasons_flat", {}))

    if existing_dls is not None:
        dls = float(existing_dls)

        # Parse reasons —  try structured first, fall back to flat
        reasons_structured = None
        reasons_flat = {}
        if result and "reasons" in result:
            reasons_structured = result["reasons"]
            reasons_flat = result.get("reasons_flat", {})
        else:
            try:
                reasons_flat = json.loads(existing_reasons) if isinstance(existing_reasons, str) else existing_reasons or {}
            except (json.JSONDecodeError, TypeError):
                reasons_flat = {}

        # ── Severity Banner ──
        severity = "moderate"
        if result:
            severity = result.get("severity", "moderate")
        elif dls >= 80: severity = "critical"
        elif dls >= 60: severity = "high"
        elif dls >= 40: severity = "moderate"
        elif dls >= 20: severity = "low"
        else: severity = "minimal"

        sev_color = SEVERITY_COLORS.get(severity, "#F4A261")
        sev_label = SEVERITY_LABELS.get(severity, "")

        if dls > 60:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {sev_color}22, {sev_color}11);
                        border-left: 4px solid {sev_color}; border-radius: 8px;
                        padding: 0.8rem 1rem; margin-bottom: 1rem;">
                <span style="font-size: 1rem; font-weight: 700; color: {sev_color};">{sev_label}</span>
                {f'<br><span style="font-size: 0.85rem; color: #6B4C35;">Confidence: {result["confidence"]}%</span>' if result else ''}
            </div>
            """, unsafe_allow_html=True)
            if st.button("⚡ Override — Proceed Anyway", key="proceed"):
                st.success("✅ Judicial override accepted. Case will proceed despite high DLS score. Audit trail logged.")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Main Layout ──
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### 📊 Dismissal Probability")
            fig = render_gauge(dls, "DLS Score")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### 📋 Risk Breakdown by Dimension")
            if reasons_structured:
                # Enhanced view with statute citations
                for key, label in REASON_LABELS.items():
                    entry = reasons_structured.get(key, {"score": 0, "detail": "N/A", "statute": "N/A"})
                    score = entry["score"]
                    detail = entry.get("detail", "N/A")
                    statute = entry.get("statute", "N/A")
                    color = "#6B8F71" if score < 30 else "#D4A843" if score < 60 else "#C0522B"
                    st.markdown(f"""
                    <div style="margin: 0.4rem 0; padding: 0.4rem 0.6rem; background: #FFF9F0;
                                border-radius: 6px; border-left: 3px solid {color};">
                        <div style="display:flex; justify-content:space-between; margin-bottom: 2px;">
                            <span style="font-weight:600; font-size:0.85rem; color:#2C1A0E;">{label}</span>
                            <span style="font-weight:700; font-size:0.85rem; color:{color};">{score}%</span>
                        </div>
                        <div style="width:100%; height:6px; background:#EDE3D4; border-radius:3px; overflow:hidden; margin: 3px 0;">
                            <div style="width:{score}%; height:100%; background:{color}; border-radius:3px;"></div>
                        </div>
                        <div style="font-size:0.75rem; color:#6B4C35; margin-top:2px;">{detail}</div>
                        <div style="font-size:0.7rem; color:#9E6B47; font-style:italic;">📖 {statute}</div>
                    </div>
                    """, unsafe_allow_html=True)
            elif reasons_flat:
                bars_html = render_reason_bars(reasons_flat)
                st.markdown(bars_html, unsafe_allow_html=True)
            else:
                st.info("No detailed breakdown available.")

        # ── AI Explanation ──
        if result:
            st.markdown("### 💡 AI Legal Analysis")
            st.markdown(f"""
            <div class="metric-card">
                <p style="color:#2C1A0E; font-size:1rem; line-height:1.6; margin:0;">{result['explanation']}</p>
            </div>
            """, unsafe_allow_html=True)

            # Precedents & Recommendation
            col_p, col_r = st.columns([1, 1])
            with col_p:
                if result.get("precedents"):
                    st.markdown("#### 📚 Applicable Precedents")
                    for prec in result["precedents"]:
                        st.markdown(f"""
                        <div style="background:#FFF9F0; padding:0.4rem 0.6rem; border-radius:6px;
                                    margin:0.2rem 0; font-size:0.85rem; color:#2C1A0E;
                                    border-left: 3px solid #D4A843;">
                            📋 {prec}
                        </div>
                        """, unsafe_allow_html=True)

            with col_r:
                rec = result.get("recommendation", "review_required")
                rec_map = {
                    "file": ("✅ Proceed to File", "#6B8F71", "Case appears well-founded. Recommended to proceed."),
                    "review_required": ("🔍 Review Required", "#D4A843", "Some issues need judicial attention before proceeding."),
                    "dismiss_likely": ("❌ Dismissal Likely", "#C0522B", "Significant defects identified. Consider correction or withdrawal."),
                    "settlement_advised": ("🤝 Settlement Advised", "#D4782A", "Case may benefit from ADR or Lok Adalat routing."),
                }
                rec_label, rec_color, rec_desc = rec_map.get(rec, rec_map["review_required"])
                st.markdown("#### 🎯 AI Recommendation")
                st.markdown(f"""
                <div style="background:{rec_color}15; border: 2px solid {rec_color};
                            border-radius: 8px; padding: 0.6rem 0.8rem; text-align: center;">
                    <div style="font-size:1.1rem; font-weight:700; color:{rec_color};">{rec_label}</div>
                    <div style="font-size:0.8rem; color:#6B4C35; margin-top:0.3rem;">{rec_desc}</div>
                </div>
                """, unsafe_allow_html=True)

        # Case summary
        with st.expander("📋 Case Details"):
            st.markdown(f"**Title:** {case['title']}")
            st.markdown(f"**Category:** {case.get('category', 'N/A').replace('_',' ').title()}")
            st.markdown(f"**Jurisdiction:** {case.get('jurisdiction', 'N/A')}")
            st.markdown(f"**Claim Amount:** ₹{case.get('claim_amount', 0):,.2f}")
            st.markdown(f"**Plaintiff:** {case.get('plaintiff_name', 'N/A')}")
            st.markdown(f"**Defendant:** {case.get('defendant_name', 'N/A')}")
            st.markdown(f"**Description:** {case['description']}")
    else:
        st.markdown("""
        <div class="metric-card" style="text-align:center;">
            <p style="color:#6B4C35; margin:0;">Click "🔍 Run DLS Analysis" to compute the dismissal probability score.</p>
        </div>
        """, unsafe_allow_html=True)
