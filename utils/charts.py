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
    """Render a NetworkX graph as an interactive Plotly scatter plot."""
    import networkx as nx

    if G.number_of_nodes() == 0:
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor="#F5F0E8",
            annotations=[dict(text="No data in graph yet", showarrow=False,
                              font=dict(size=16, color="#6B4C35"))]
        )
        return fig

    pos = nx.spring_layout(G, seed=42, k=2)
    centrality = nx.degree_centrality(G)

    edge_x, edge_y = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    node_x = [pos[n][0] for n in G.nodes()]
    node_y = [pos[n][1] for n in G.nodes()]
    node_size = [10 + centrality.get(n, 0) * 60 for n in G.nodes()]
    node_color = [
        "#C0522B" if G.nodes[n].get("case_count", 0) > 5 else "#8B5E3C"
        for n in G.nodes()
    ]
    node_text = [
        f"{G.nodes[n].get('label', n)}<br>Cases: {G.nodes[n].get('case_count', 0)}"
        for n in G.nodes()
    ]

    fig = go.Figure(data=[
        go.Scatter(
            x=edge_x, y=edge_y, mode="lines",
            line=dict(width=1, color="#A0522D"),
            hoverinfo="none",
        ),
        go.Scatter(
            x=node_x, y=node_y, mode="markers+text",
            marker=dict(
                size=node_size, color=node_color,
                line=dict(width=2, color="#F5F0E8"),
            ),
            text=[G.nodes[n].get("label", n) for n in G.nodes()],
            hovertext=node_text,
            hoverinfo="text",
            textfont=dict(color="#2C1A0E", size=10),
        ),
    ])
    fig.update_layout(
        paper_bgcolor="#F5F0E8",
        plot_bgcolor="#F5F0E8",
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=500,
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
