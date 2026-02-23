# utils/charts.py — Plotly visualization helpers
import plotly.graph_objects as go
import numpy as np
import math


def render_gauge(value: float, title: str = "Score",
                 ranges: list[tuple] | None = None,
                 max_val: int = 100) -> go.Figure:
    """
    Render a Plotly gauge indicator.
    ranges: list of (threshold, color, label) tuples — e.g. [(30,'green','Low'), (70,'amber','Med'), (100,'red','High')]
    """
    if ranges is None:
        ranges = [
            (30, "#6B8F71", "Low"),
            (70, "#D4A843", "Medium"),
            (100, "#C0522B", "High"),
        ]

    steps = []
    prev = 0
    for threshold, color, label in ranges:
        steps.append(dict(range=[prev, threshold], color=color, name=label))
        prev = threshold

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 16, "color": "#2C1A0E", "family": "Inter"}},
        number={"font": {"size": 42, "color": "#2C1A0E", "family": "Inter"}},
        gauge={
            "axis": {"range": [0, max_val], "tickcolor": "#6B4C35"},
            "bar": {"color": "#C0522B", "thickness": 0.3},
            "bgcolor": "#EDE3D4",
            "borderwidth": 2,
            "bordercolor": "#8B5E3C",
            "steps": steps,
            "threshold": {
                "line": {"color": "#B03A2E", "width": 4},
                "thickness": 0.8,
                "value": value,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor="#F5F0E8",
        plot_bgcolor="#F5F0E8",
        font={"family": "Inter"},
        height=280,
        margin=dict(l=30, r=30, t=60, b=20),
    )
    return fig


def render_dna_helix(vector: list[float], twin_vector: list[float] = None) -> go.Figure:
    """
    Render a radar chart comparing the case DNA vector against its twin.
    Each axis = one of the 6 DNA dimensions. Shows overlap = why they matched.
    If no twin_vector is provided, shows just the case's own profile.
    """
    labels = ["Category", "Jurisdiction", "Claim Size", "Evidence", "Emotion", "Novelty"]
    # Close the radar polygon
    values_case = list(vector) + [vector[0]]
    labels_closed = labels + [labels[0]]

    fig = go.Figure()

    # New case trace
    fig.add_trace(go.Scatterpolar(
        r=values_case,
        theta=labels_closed,
        fill="toself",
        fillcolor="rgba(192, 82, 43, 0.2)",
        line=dict(color="#C0522B", width=3),
        marker=dict(size=8, color="#C0522B"),
        name="📋 This Case",
    ))

    # Twin case trace (if available)
    if twin_vector:
        values_twin = list(twin_vector) + [twin_vector[0]]
        fig.add_trace(go.Scatterpolar(
            r=values_twin,
            theta=labels_closed,
            fill="toself",
            fillcolor="rgba(212, 168, 67, 0.15)",
            line=dict(color="#D4A843", width=3, dash="dash"),
            marker=dict(size=8, color="#D4A843"),
            name="🔗 Case Twin",
        ))

    fig.update_layout(
        polar=dict(
            bgcolor="#EDE3D4",
            radialaxis=dict(
                visible=True, range=[0, 1],
                gridcolor="rgba(139, 94, 60, 0.27)",
                tickfont=dict(size=10, color="#6B4C35"),
            ),
            angularaxis=dict(
                gridcolor="rgba(139, 94, 60, 0.27)",
                tickfont=dict(size=12, color="#2C1A0E", family="Inter"),
            ),
        ),
        paper_bgcolor="#F5F0E8",
        font=dict(family="Inter"),
        showlegend=True,
        legend=dict(
            x=0.5, y=-0.15, xanchor="center",
            font=dict(size=12, color="#2C1A0E"),
            orientation="h",
        ),
        height=400,
        margin=dict(l=60, r=60, t=30, b=60),
    )
    return fig


def render_conflict_graph(G) -> go.Figure:
    """Render a NetworkX graph as a polished, consolidated Plotly scatter plot."""
    import networkx as nx
    from graph.conflict_graph import get_consolidated_edges

    # ── empty-graph guard ────────────────────────────────────────
    if G.number_of_nodes() == 0:
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor="#1a1a2e",
            plot_bgcolor="#1a1a2e",
            annotations=[dict(text="No data in graph yet", showarrow=False,
                              font=dict(size=16, color="#e0d6c8"))],
        )
        return fig

    # ── layout ───────────────────────────────────────────────────
    try:
        pos = nx.kamada_kawai_layout(G)
    except Exception:
        pos = nx.spring_layout(G, seed=42, k=2.5)

    # ── entity-type color palette ────────────────────────────────
    TYPE_COLORS = {
        "person":     "#4ecdc4",   # teal
        "company":    "#f0a500",   # amber
        "government": "#a855f7",   # purple
        "unknown":    "#94a3b8",   # slate gray
    }

    # ── consolidated edges ───────────────────────────────────────
    consolidated = get_consolidated_edges(G)
    max_weight = max((e["weight"] for e in consolidated), default=1)

    edge_traces = []
    edge_annotations = []

    for edge in consolidated:
        u, v = edge["source"], edge["target"]
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        w = edge["weight"]

        # Width: 1.5 → 7 based on weight
        line_width = 1.5 + (w / max(max_weight, 1)) * 5.5

        # Color: light warm gray → hot red based on weight
        ratio = (w - 1) / max(max_weight - 1, 1)
        r = int(160 + ratio * 95)     # 160 → 255
        g = int(140 - ratio * 80)     # 140 → 60
        b = int(120 - ratio * 80)     # 120 → 40
        edge_color = f"rgba({r},{g},{b},0.6)"

        # Hover text for edge
        case_str = ", ".join(edge["case_ids"][:5])
        types_str = ", ".join(sorted(edge["edge_types"]))
        hover = f"Cases: {w}<br>{case_str}<br>Types: {types_str}"

        edge_traces.append(go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            mode="lines",
            line=dict(width=line_width, color=edge_color),
            hoverinfo="text",
            hovertext=hover,
            showlegend=False,
        ))

        # Annotation label for multi-case edges
        if w >= 2:
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            edge_annotations.append(dict(
                x=mx, y=my, text=f"×{w}",
                showarrow=False,
                font=dict(size=10, color="#fbbf24", family="Inter, sans-serif"),
                bgcolor="rgba(26,26,46,0.7)",
                borderpad=2,
            ))

    # ── nodes ────────────────────────────────────────────────────
    node_x = [pos[n][0] for n in G.nodes()]
    node_y = [pos[n][1] for n in G.nodes()]

    case_counts = [G.nodes[n].get("case_count", 0) for n in G.nodes()]
    max_cc = max(case_counts) if case_counts else 1

    node_size = [
        14 + (G.nodes[n].get("case_count", 0) / max(max_cc, 1)) * 36
        for n in G.nodes()
    ]
    node_color = [
        TYPE_COLORS.get(G.nodes[n].get("entity_type", "unknown"), TYPE_COLORS["unknown"])
        for n in G.nodes()
    ]
    node_border_width = [
        3 if G.nodes[n].get("case_count", 0) >= 4 else 1.5
        for n in G.nodes()
    ]
    node_border_color = [
        "#ef4444" if G.nodes[n].get("case_count", 0) >= 4 else "rgba(255,255,255,0.3)"
        for n in G.nodes()
    ]

    node_text = [G.nodes[n].get("label", n) for n in G.nodes()]
    hover_text = [
        f"<b>{G.nodes[n].get('label', n)}</b><br>"
        f"Type: {G.nodes[n].get('entity_type', 'unknown').title()}<br>"
        f"Cases: {G.nodes[n].get('case_count', 0)}<br>"
        f"Connections: {G.degree(n)}"
        for n in G.nodes()
    ]

    # Glow layer for high-involvement nodes
    glow_x, glow_y, glow_size, glow_color = [], [], [], []
    for n in G.nodes():
        if G.nodes[n].get("case_count", 0) >= 4:
            glow_x.append(pos[n][0])
            glow_y.append(pos[n][1])
            s = 14 + (G.nodes[n].get("case_count", 0) / max(max_cc, 1)) * 36
            glow_size.append(s + 18)
            glow_color.append("rgba(239,68,68,0.15)")

    glow_trace = go.Scatter(
        x=glow_x, y=glow_y, mode="markers",
        marker=dict(size=glow_size, color=glow_color, line=dict(width=0)),
        hoverinfo="skip", showlegend=False,
    ) if glow_x else None

    node_trace = go.Scatter(
        x=node_x, y=node_y, mode="markers+text",
        marker=dict(
            size=node_size, color=node_color,
            line=dict(width=node_border_width, color=node_border_color),
        ),
        text=node_text,
        textposition="top center",
        textfont=dict(color="#e0d6c8", size=11, family="Inter, sans-serif"),
        hovertext=hover_text,
        hoverinfo="text",
        showlegend=False,
    )

    # ── assemble figure ──────────────────────────────────────────
    data = edge_traces
    if glow_trace:
        data.append(glow_trace)
    data.append(node_trace)

    # Legend entries for entity types (invisible points for legend only)
    for etype, color in TYPE_COLORS.items():
        has_type = any(
            G.nodes[n].get("entity_type", "unknown") == etype for n in G.nodes()
        )
        if has_type:
            data.append(go.Scatter(
                x=[None], y=[None], mode="markers",
                marker=dict(size=10, color=color),
                name=etype.title(),
                showlegend=True,
            ))

    fig = go.Figure(data=data)

    fig.update_layout(
        paper_bgcolor="#1a1a2e",
        plot_bgcolor="#1a1a2e",
        showlegend=True,
        legend=dict(
            font=dict(color="#e0d6c8", size=11, family="Inter, sans-serif"),
            bgcolor="rgba(26,26,46,0.8)",
            bordercolor="rgba(255,255,255,0.1)",
            borderwidth=1,
            orientation="h",
            yanchor="bottom", y=1.02, xanchor="center", x=0.5,
        ),
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=550,
        annotations=edge_annotations,
        hoverlabel=dict(
            bgcolor="#2C1A0E", font_size=12, font_color="#e0d6c8",
            font_family="Inter, sans-serif",
        ),
    )
    return fig


def render_emotion_timeline(turns: list[int], temperatures: list[float]) -> go.Figure:
    """Render an emotion temperature timeline chart."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=turns, y=temperatures,
        mode="lines+markers",
        line=dict(color="#C0522B", width=3, shape="spline"),
        marker=dict(size=10, color="#C0522B", line=dict(width=2, color="#F5F0E8")),
        fill="tozeroy",
        fillcolor="rgba(192, 82, 43, 0.1)",
        name="Emotion Temperature",
    ))

    # Threshold lines
    fig.add_hline(y=30, line_dash="dash", line_color="#6B8F71",
                  annotation_text="Calm", annotation_position="right")
    fig.add_hline(y=70, line_dash="dash", line_color="#B03A2E",
                  annotation_text="Critical", annotation_position="right")

    fig.update_layout(
        paper_bgcolor="#F5F0E8",
        plot_bgcolor="#F5F0E8",
        font=dict(family="Inter", color="#2C1A0E"),
        xaxis_title="Turn",
        yaxis_title="Temperature",
        yaxis=dict(range=[0, 100]),
        height=300,
        margin=dict(l=40, r=20, t=20, b=40),
    )
    return fig


def render_reason_bars(reasons: dict) -> str:
    """Return HTML for horizontal reason breakdown bars."""
    html = ""
    labels = {
        "lack_of_jurisdiction": "Jurisdiction",
        "statute_of_limitations": "Statute of Limitations",
        "insufficient_evidence": "Insufficient Evidence",
        "frivolous_claim": "Frivolous Claim",
        "procedural_defect": "Procedural Defect",
    }
    for key, label in labels.items():
        val = reasons.get(key, 0)
        color = "#6B8F71" if val < 30 else "#D4A843" if val < 70 else "#C0522B"
        html += f"""
        <div style="margin: 0.4rem 0;">
            <div style="display:flex; justify-content:space-between; font-size:0.85rem; color:#2C1A0E; font-weight:500;">
                <span>{label}</span><span>{val}%</span>
            </div>
            <div style="width:100%; height:12px; background:#EDE3D4; border-radius:6px; overflow:hidden;">
                <div style="width:{val}%; height:100%; background:{color}; border-radius:6px;
                            transition: width 0.8s ease;"></div>
            </div>
        </div>
        """
    return html
