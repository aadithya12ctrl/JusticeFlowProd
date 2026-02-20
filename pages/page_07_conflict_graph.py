# pages/page_07_conflict_graph.py — Quantum Conflict Graph Viewer
import streamlit as st
import json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.theme import page_header
from utils.charts import render_conflict_graph
from config import DB_PATH
from graph.conflict_graph import build_graph, detect_repeat_offenders, get_entity_history, detect_systematic_patterns


def render():
    page_header("Conflict Graph", "Visualize dispute networks and detect systemic patterns")

    G = build_graph(DB_PATH)

    if G.number_of_nodes() == 0:
        st.info("📭 No entities in the graph yet. File cases or seed demo data to populate the graph.")
        return

    # Stats row
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card" style="text-align:center;"><h3>Nodes</h3><div class="value">{G.number_of_nodes()}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card" style="text-align:center;"><h3>Edges</h3><div class="value">{G.number_of_edges()}</div></div>', unsafe_allow_html=True)
    with c3:
        offenders = detect_repeat_offenders(G, threshold=3)
        st.markdown(f'<div class="metric-card" style="text-align:center;border-left-color:#B03A2E;"><h3>Repeat Offenders</h3><div class="value" style="color:#B03A2E;">{len(offenders)}</div></div>', unsafe_allow_html=True)

    # Graph visualization
    st.markdown("### 🕸️ Network Visualization")
    fig = render_conflict_graph(G)
    st.plotly_chart(fig, use_container_width=True)

    # Systematic pattern alerts
    patterns = detect_systematic_patterns(G)
    if patterns:
        for p in patterns:
            st.markdown(f"""
            <div class="warning-banner">
                ⚠️ Potential systematic filing pattern detected: <strong>{p['label']}</strong>
                has {p['target_count']} cases of type "{p['pattern']}" against different parties.
            </div>
            """, unsafe_allow_html=True)

    # Repeat offenders panel
    col_graph, col_panel = st.columns([2, 1])
    with col_panel:
        st.markdown("### 🚨 Repeat Offenders")
        if offenders:
            for o in offenders:
                color = "#B03A2E" if o["case_count"] >= 5 else "#D4A843"
                st.markdown(f"""
                <div class="metric-card" style="border-left-color:{color};">
                    <div style="font-weight:700;color:#2C1A0E;">{o['label']}</div>
                    <div style="display:flex;justify-content:space-between;">
                        <span style="color:#6B4C35;font-size:0.85rem;">{o['entity_type'].title()}</span>
                        <span style="color:{color};font-weight:700;">{o['case_count']} cases</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No repeat offenders detected (threshold: 3+ cases).")

    # Entity inspector
    with col_graph:
        st.markdown("### 🔍 Entity Inspector")
        node_labels = {G.nodes[n].get("label", n): n for n in G.nodes()}
        selected = st.selectbox("Select an entity", list(node_labels.keys()))
        if selected:
            entity_id = node_labels[selected]
            history = get_entity_history(G, entity_id)

            st.markdown(f"""
            <div class="metric-card">
                <h3>{selected}</h3>
                <div style="display:flex;gap:1rem;">
                    <span style="color:#6B4C35;">Connected nodes: <strong>{history['node_count']}</strong></span>
                    <span style="color:#6B4C35;">Relationships: <strong>{history['edge_count']}</strong></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if history.get("edges"):
                st.markdown("**Dispute History:**")
                for edge in history["edges"]:
                    st.markdown(f"- **{edge['from']}** → **{edge['to']}** ({edge['edge_type'].replace('_',' ').title()}) — Case #{edge['case_id']}")
