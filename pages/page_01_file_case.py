# pages/page_01_file_case.py — Case submission form + DNA fingerprinting
import streamlit as st
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.theme import page_header, metric_card
from utils.charts import render_dna_helix
from config import get_llm, CASE_CATEGORIES
from db.database import insert_case, update_case, get_historical_cases, get_case
from agents.dna_agent import build_dna_vector, find_case_twin


def render():
    page_header("File a Case", "Submit a new dispute for AI-powered analysis")

    with st.form("case_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("📋 Case Title", placeholder="e.g. Landlord Heating Dispute")
            plaintiff_name = st.text_input("👤 Plaintiff Name", placeholder="e.g. John Smith")
            category = st.selectbox("📂 Category", CASE_CATEGORIES,
                                    format_func=lambda x: x.replace("_", " ").title())
        with col2:
            claim_amount = st.number_input("💰 Claim Amount ($)", min_value=0.0, step=100.0, value=5000.0)
            defendant_name = st.text_input("👤 Defendant Name", placeholder="e.g. Greenfield Properties LLC")
            jurisdiction = st.text_input("🏛️ Jurisdiction", placeholder="e.g. Municipal Court")

        description = st.text_area(
            "📝 Case Description",
            height=150,
            placeholder="Describe the dispute in detail. Include relevant dates, events, and damages..."
        )

        submitted = st.form_submit_button("⚖️ Submit Case & Generate DNA", use_container_width=True)

    if submitted:
        if not title or not description or not plaintiff_name or not defendant_name:
            st.error("⚠️ Please fill in all required fields: Title, Description, Plaintiff, and Defendant.")
            return

        with st.spinner("🧬 Filing case and computing DNA vector..."):
            # Insert case
            case_id = insert_case(
                title=title,
                description=description,
                category=category,
                jurisdiction=jurisdiction,
                claim_amount=claim_amount,
                plaintiff_name=plaintiff_name,
                defendant_name=defendant_name,
            )

            # Build DNA vector
            try:
                llm = get_llm()
                case_text = f"Title: {title}\nCategory: {category}\nJurisdiction: {jurisdiction}\nClaim: ${claim_amount}\nDescription: {description}"
                dna_vector = build_dna_vector(case_text, llm)
            except Exception as e:
                st.warning(f"⚠️ LLM call failed, using default vector. Error: {str(e)[:100]}")
                dna_vector = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5]

            # Save DNA vector
            update_case(case_id, dna_vector=json.dumps(dna_vector), status="scored")

            # Find case twin
            historical = get_historical_cases()
            twin, similarity = find_case_twin(dna_vector, historical)

        # Success message
        st.markdown(f"""
        <div class="success-card">
            ✅ Case #{case_id} filed successfully! DNA vector computed.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Results layout
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### 🧬 Case DNA Vector")
            labels = ["Category", "Jurisdiction", "Claim Bucket", "Evidence", "Emotion", "Novelty"]
            for label, val in zip(labels, dna_vector):
                color = "#6B8F71" if val < 0.4 else "#D4A843" if val < 0.7 else "#C0522B"
                st.markdown(f"""
                <div style="margin: 0.3rem 0;">
                    <div style="display:flex; justify-content:space-between; font-size:0.85rem; color:#2C1A0E;">
                        <span>{label}</span><span>{val:.2f}</span>
                    </div>
                    <div style="width:100%; height:8px; background:#EDE3D4; border-radius:4px; overflow:hidden;">
                        <div style="width:{val*100:.0f}%; height:100%; background:{color}; border-radius:4px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            if twin and similarity > 0:
                st.markdown("### 🔗 Case Twin Found")
                st.markdown(f"""
                <div class="case-card">
                    <div class="case-title">📋 {twin.get('id', 'Unknown')} — {twin.get('category', '').replace('_',' ').title()}</div>
                    <div style="font-size:1.5rem; font-weight:700; color:#C0522B; margin:0.5rem 0;">
                        {similarity*100:.1f}% Match
                    </div>
                    <p style="color:#6B4C35; font-size:0.9rem; margin:0.5rem 0;">{twin.get('summary', '')}</p>
                    <div style="background:#EDE3D4; padding:0.5rem 0.8rem; border-radius:6px; margin-top:0.5rem;">
                        <strong style="color:#2C1A0E;">Outcome:</strong>
                        <span style="color:#6B4C35;"> {twin.get('outcome', 'N/A')}</span>
                    </div>
                    <div style="font-size:0.8rem; color:#6B4C35; margin-top:0.3rem;">
                        📅 {twin.get('year', '')} · 🏛️ {twin.get('jurisdiction', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No similar historical case found in the database. Seed demo data to enable case matching.")

        # DNA Comparison Radar Chart
        st.markdown("### 🧬 Case DNA Comparison")
        twin_vec = None
        if twin:
            try:
                twin_vec = json.loads(twin["dna_vector"]) if isinstance(twin["dna_vector"], str) else twin["dna_vector"]
            except (json.JSONDecodeError, TypeError):
                twin_vec = None
        fig = render_dna_helix(dna_vector, twin_vector=twin_vec)
        st.plotly_chart(fig, use_container_width=True)

        # Store in session for other pages
        st.session_state["last_case_id"] = case_id
