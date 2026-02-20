# pages/page_04_emotion_monitor.py — Emotional Intelligence Dashboard
import streamlit as st
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.theme import page_header
from utils.charts import render_gauge, render_emotion_timeline
from config import get_llm
from db.database import get_all_cases, get_case, update_case, get_negotiation_log
from agents.emotion_agent import analyze_emotion, EMOTION_COLORS, EMOTION_ICONS


def render():
    page_header("Emotion Monitor", "Real-time emotional temperature analysis")

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

    # Analyze button
    if st.button("💭 Analyze Emotional Temperature", use_container_width=True):
        with st.spinner("💭 Analyzing emotional content..."):
            try:
                llm = get_llm()
                result = analyze_emotion(case["description"], llm)
            except Exception as e:
                st.error(f"⚠️ Analysis failed: {str(e)[:100]}")
                return

            # Save to DB
            update_case(case_id, emotional_temp=result["temperature"])

        temperature = result["temperature"]
        emotion = result["dominant_emotion"]
        recommendation = result["recommendation"]

        # Cooling-off alert
        if temperature > 70:
            st.markdown(f"""
            <div class="warning-banner" style="animation: pulse-border 2s infinite;">
                ⚠️ Party appears highly emotional (Temperature: {temperature}/100).
                Recommend 10-minute cooling-off period before proceeding.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Main layout
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### 🌡️ Emotional Temperature")
            ranges = [
                (30, "#6B8F71", "Calm"),
                (60, "#D4A843", "Elevated"),
                (100, "#B03A2E", "Critical"),
            ]
            fig = render_gauge(temperature, "Temperature", ranges)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### 💭 Dominant Emotion")
            icon = EMOTION_ICONS.get(emotion, "😐")
            color = EMOTION_COLORS.get(emotion, "#6B4C35")
            st.markdown(f"""
            <div class="metric-card" style="text-align:center; border-left-color:{color};">
                <div style="font-size:3rem; margin-bottom:0.5rem;">{icon}</div>
                <div class="value" style="color:{color}; text-transform:capitalize;">{emotion}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### 💡 Mediator Recommendation")
            st.markdown(f"""
            <div class="metric-card" style="border-left-color:#D4A843;">
                <p style="color:#2C1A0E; font-size:0.95rem; line-height:1.5; margin:0;">
                    {recommendation}
                </p>
            </div>
            """, unsafe_allow_html=True)

    # Negotiation emotion timeline
    neg_log = get_negotiation_log(case_id)
    if neg_log:
        st.markdown("---")
        st.markdown("### 📈 Negotiation Emotion Timeline")

        if st.button("📊 Analyze Negotiation Emotions", key="analyze_neg"):
            with st.spinner("Analyzing emotions across negotiation turns..."):
                llm = get_llm()
                turns = []
                temps = []
                for i, entry in enumerate(neg_log):
                    try:
                        result = analyze_emotion(entry["message"], llm)
                        turns.append(i + 1)
                        temps.append(result["temperature"])
                    except Exception:
                        turns.append(i + 1)
                        temps.append(50)

                fig = render_emotion_timeline(turns, temps)
                st.plotly_chart(fig, use_container_width=True)

                # Summary
                avg_temp = sum(temps) / len(temps) if temps else 0
                max_temp = max(temps) if temps else 0
                st.markdown(f"""
                <div style="display:flex; gap:1rem;">
                    <div class="metric-card" style="flex:1; text-align:center;">
                        <h3>Average Temperature</h3>
                        <div class="value">{avg_temp:.0f}</div>
                    </div>
                    <div class="metric-card" style="flex:1; text-align:center;">
                        <h3>Peak Temperature</h3>
                        <div class="value" style="color:#B03A2E;">{max_temp}</div>
                    </div>
                    <div class="metric-card" style="flex:1; text-align:center;">
                        <h3>Turns Analyzed</h3>
                        <div class="value">{len(turns)}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Existing emotional temp display
    if case.get("emotional_temp") is not None:
        st.markdown("---")
        temp = float(case["emotional_temp"])
        color = "#6B8F71" if temp < 30 else "#D4A843" if temp < 60 else "#B03A2E"
        st.markdown(f"""
        <div class="metric-card" style="border-left-color:{color};">
            <h3>Last Recorded Temperature</h3>
            <div class="value" style="color:{color};">{temp:.0f}/100</div>
        </div>
        """, unsafe_allow_html=True)
