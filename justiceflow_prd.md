# ⚖️ JusticeFlow — Product Requirements Document

> **Hackathon Build · 7-Day Sprint**
> Theme: Terracotta · Rust · Cream · Brown · Warm Beige
> Stack: Python · Streamlit · SQLite · NetworkX · LangChain · LangGraph · Groq LLM

---

## 1. Product Overview

**JusticeFlow** is an AI-powered dispute resolution platform that streamlines court intake, predicts case outcomes, mediates between parties autonomously, and surfaces systemic legal abuse patterns — all within a single Streamlit application backed by SQLite and Groq-powered LLM agents.

### Vision Statement
Transform dispute resolution from a slow, paper-bound process into an intelligent, real-time system that saves courts time, guides parties toward fair settlements, and exposes bad actors through relational graph intelligence.

### Design Language
| Token | Value |
|---|---|
| Primary | `#C0522B` — Terracotta Red |
| Secondary | `#8B5E3C` — Warm Brown |
| Background | `#F5F0E8` — Cream |
| Surface | `#EDE3D4` — Beige |
| Accent | `#A0522D` — Sienna |
| Text Dark | `#2C1A0E` — Dark Espresso |
| Text Light | `#6B4C35` — Mocha |
| Success | `#6B8F71` — Sage Green |
| Warning | `#D4A843` — Amber |
| Danger | `#B03A2E` — Deep Red |

All Streamlit pages inject a shared `custom_css()` function that overrides default theme tokens with the palette above.

---

## 2. Architecture Overview

```
justiceflow/
├── app.py                    # Streamlit entry point, sidebar nav
├── config.py                 # Constants, DB path, Groq API key
├── db/
│   ├── schema.sql            # All table definitions
│   └── database.py           # SQLite connection + helpers
├── agents/
│   ├── dna_agent.py          # Case DNA fingerprinting (LangChain)
│   ├── dls_agent.py          # Dismissal Likelihood Score (LangChain)
│   ├── negotiation_graph.py  # LangGraph multi-agent negotiation
│   └── emotion_agent.py      # Sentiment analysis (LangChain)
├── graph/
│   └── conflict_graph.py     # NetworkX graph builder + queries
├── pages/
│   ├── 01_file_case.py       # Case submission form
│   ├── 02_dls_engine.py      # DLS gauge + warnings
│   ├── 03_negotiation.py     # Autonomous negotiation sandbox
│   ├── 04_emotion_monitor.py # Emotional temperature dashboard
│   ├── 05_auto_filter.py     # Jurisdiction & triviality filter
│   ├── 06_judge_cockpit.py   # Judge summary dashboard
│   └── 07_conflict_graph.py  # Quantum conflict graph viewer
├── utils/
│   ├── theme.py              # CSS injection + color helpers
│   ├── charts.py             # Plotly gauge, DNA helix, graph viz
│   └── seed_data.py          # Demo data population script
└── requirements.txt
```

### Technology Decisions

| Concern | Choice | Rationale |
|---|---|---|
| UI Framework | Streamlit | Rapid prototyping; single-file pages |
| Database | SQLite (via `sqlite3`) | Zero config; fully self-contained |
| Graph Engine | NetworkX | Pure Python; rich graph algorithms |
| LLM Runtime | Groq (`groq` SDK) | Ultra-fast inference; free tier available |
| LLM Orchestration | LangChain | Prompt management, output parsers |
| Multi-Agent Flow | LangGraph | Stateful agent graphs; negotiation loop |
| Visualization | Plotly (built into Streamlit) | Gauge charts, scatter for graph nodes |
| NLP / Sentiment | TextBlob or LangChain LLMChain | Lightweight; no external API needed |

> **No external paid APIs, no cloud databases, no Docker required.** Everything runs locally with `streamlit run app.py`.

---

## 3. Database Schema

```sql
-- schema.sql

CREATE TABLE IF NOT EXISTS cases (
    id              TEXT PRIMARY KEY,       -- UUID
    title           TEXT NOT NULL,
    description     TEXT NOT NULL,
    category        TEXT,                   -- landlord-tenant, employment, contract, etc.
    jurisdiction    TEXT,
    claim_amount    REAL,
    plaintiff_id    TEXT,
    defendant_id    TEXT,
    status          TEXT DEFAULT 'intake',  -- intake, filtered, scored, negotiating, resolved, escalated
    filed_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    dls_score       REAL,
    dls_reasons     TEXT,                   -- JSON array
    dna_vector      TEXT,                   -- JSON serialized float list
    emotional_temp  REAL,
    filter_result   TEXT,                   -- JSON: {passed, reason, routing}
    settlement_text TEXT,
    ai_outcome      TEXT,
    ai_confidence   REAL
);

CREATE TABLE IF NOT EXISTS entities (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    type            TEXT,                   -- person, company, court, government
    registered_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS case_edges (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id         TEXT,
    entity_a        TEXT,
    entity_b        TEXT,
    edge_type       TEXT,                   -- plaintiff, defendant, settled, dismissed
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS negotiation_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id         TEXT,
    turn            INTEGER,
    speaker         TEXT,                   -- 'agent_plaintiff' | 'agent_defendant' | 'system'
    message         TEXT,
    timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS historical_cases (
    id              TEXT PRIMARY KEY,
    summary         TEXT,
    category        TEXT,
    outcome         TEXT,
    dna_vector      TEXT,                   -- JSON float list for cosine similarity
    jurisdiction    TEXT,
    year            INTEGER
);
```

---

## 4. Feature Specifications

---

### Feature 1 — Case DNA Fingerprinting

**Page:** `pages/01_file_case.py` + `agents/dna_agent.py`

#### What it does
When a user submits a case, a LangChain chain prompts Groq to extract structured attributes (category, jurisdiction, emotional intensity 0–10, evidence strength 0–10, claim bucket) and serializes them as a normalized float vector. The vector is stored in `cases.dna_vector`. A cosine similarity search against `historical_cases.dna_vector` surfaces the top "Case Twin."

#### Implementation

```python
# agents/dna_agent.py
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
import json, math

DNA_PROMPT = PromptTemplate.from_template("""
You are a legal classification engine. Given this case description, extract a JSON object with these fields:
- category: one of [landlord_tenant, employment, contract, personal_injury, family, small_claims, other]
- jurisdiction_score: 0.0–1.0 (how clearly the correct court is stated)
- claim_bucket: 1=<$1k, 2=$1k–10k, 3=$10k–100k, 4=>$100k
- evidence_strength: 0.0–1.0
- emotional_intensity: 0.0–1.0
- novelty: 0.0–1.0 (how unusual the claim is)

Return ONLY valid JSON. Case: {case_text}
""")

def build_dna_vector(case_text: str, llm) -> list[float]:
    chain = LLMChain(llm=llm, prompt=DNA_PROMPT)
    raw = chain.run(case_text=case_text)
    data = json.loads(raw)
    category_map = {"landlord_tenant":0.1, "employment":0.2, "contract":0.3,
                    "personal_injury":0.4, "family":0.5, "small_claims":0.6, "other":0.9}
    return [
        category_map.get(data["category"], 0.9),
        float(data["jurisdiction_score"]),
        float(data["claim_bucket"]) / 4.0,
        float(data["evidence_strength"]),
        float(data["emotional_intensity"]),
        float(data["novelty"])
    ]

def cosine_similarity(a: list, b: list) -> float:
    dot = sum(x*y for x,y in zip(a,b))
    mag_a = math.sqrt(sum(x**2 for x in a))
    mag_b = math.sqrt(sum(x**2 for x in b))
    return dot / (mag_a * mag_b + 1e-9)
```

#### UI
- Streamlit form: title, description, plaintiff name, defendant name, claim amount, category dropdown, jurisdiction text field.
- On submit: spinner → DNA vector computed → Case Twin card appears (terracotta bordered card showing the matched historical case, outcome, and similarity %).
- DNA helix visualization: a Plotly 3D scatter plot with two helical strands colored in terracotta and cream — purely aesthetic, rendered from the 6D vector mapped to helix parameters.

---

### Feature 2 — AI Dismissal Probability Engine

**Page:** `pages/02_dls_engine.py` + `agents/dls_agent.py`

#### What it does
A LangChain LLMChain analyzes the submitted case and outputs a structured JSON with an overall DLS score (0–100) and per-reason breakdown. If DLS > 75 the UI shows a full-screen warning with a detailed explanation.

#### Implementation

```python
# agents/dls_agent.py
DLS_PROMPT = PromptTemplate.from_template("""
You are a senior court clerk. Analyze this case and estimate dismissal probability.
Return JSON only with this schema:
{{
  "dls": <int 0-100>,
  "reasons": {{
    "lack_of_jurisdiction": <int 0-100>,
    "statute_of_limitations": <int 0-100>,
    "insufficient_evidence": <int 0-100>,
    "frivolous_claim": <int 0-100>,
    "procedural_defect": <int 0-100>
  }},
  "explanation": "<2-3 sentence plain English summary>"
}}
Case title: {title}
Case description: {description}
Jurisdiction: {jurisdiction}
Claim amount: {claim_amount}
""")
```

#### UI
- **Gauge meter**: Plotly `go.Indicator` in gauge mode. Color scale: `#6B8F71` (0–30) → `#D4A843` (30–70) → `#C0522B` (70–100). Rendered on a cream background card.
- **Reason breakdown**: Five horizontal progress bars, each labeled and color-coded.
- **Warning banner**: If DLS > 75, a full-width terracotta banner with bold warning text and the LLM explanation. A "Proceed Anyway" button allows override.
- Score and reasons saved to `cases.dls_score` and `cases.dls_reasons`.

---

### Feature 3 — Autonomous Negotiation Sandbox

**Page:** `pages/03_negotiation.py` + `agents/negotiation_graph.py`

#### What it does
A **LangGraph** `StateGraph` orchestrates two specialized agents — `AgentPlaintiff` and `AgentDefendant` — in an alternating turn loop. Each agent is primed with its party's stated interests and constraints. They exchange offers until convergence (both accept) or max turns (10). A `MediatorNode` monitors for convergence and injects compromise hints when agents are far apart. The final accepted offer is formatted as a settlement agreement.

#### LangGraph State Schema

```python
# agents/negotiation_graph.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class NegotiationState(TypedDict):
    case_id: str
    case_summary: str
    plaintiff_interests: str
    defendant_interests: str
    turn: int
    max_turns: int
    history: Annotated[list[dict], operator.add]  # [{speaker, message, offer_amount}]
    current_offer: float
    plaintiff_accepted: bool
    defendant_accepted: bool
    settlement_text: str
    status: str  # negotiating | settled | failed

def plaintiff_node(state: NegotiationState) -> NegotiationState: ...
def defendant_node(state: NegotiationState) -> NegotiationState: ...
def mediator_node(state: NegotiationState) -> NegotiationState: ...
def should_continue(state: NegotiationState) -> str: ...

graph = StateGraph(NegotiationState)
graph.add_node("plaintiff", plaintiff_node)
graph.add_node("defendant", defendant_node)
graph.add_node("mediator", mediator_node)
graph.set_entry_point("plaintiff")
graph.add_conditional_edges("mediator", should_continue,
    {"continue": "plaintiff", "settled": END, "failed": END})
graph.add_edge("plaintiff", "mediator")
graph.add_edge("defendant", "mediator")
```

#### Agent Prompts
Each agent receives: case summary, its party's interests, current offer on the table, and full negotiation history. It responds with a counter-offer and brief justification citing relevant legal principle.

#### UI
- Two-column chat layout: plaintiff (left, sienna-tinted) vs defendant (right, brown-tinted).
- Each turn streams into a `st.chat_message` bubble in real time using `st.empty()` + generator.
- A center "Current Offer" display updates after each turn with a large terracotta number.
- **Accept / Override** buttons visible to both parties.
- On settlement: a formatted agreement text box appears with a "Download Agreement" button that saves to a `.txt` file.
- Full transcript saved to `negotiation_log` table.

---

### Feature 4 — Emotional Intelligence Layer

**Page:** `pages/04_emotion_monitor.py` + `agents/emotion_agent.py`

#### What it does
Runs sentiment analysis on the case filing text using a LangChain chain with Groq. Produces an emotional temperature score (0–100) and tags the dominant emotion (anger, fear, grief, frustration, neutral). During the negotiation, each new message from a party is re-scored and the meter updates live.

#### Implementation

```python
# agents/emotion_agent.py
EMOTION_PROMPT = PromptTemplate.from_template("""
Analyze the emotional state conveyed in this legal filing or message.
Return JSON only:
{{
  "temperature": <int 0-100>,  // 0=calm, 100=explosive
  "dominant_emotion": "<anger|fear|grief|frustration|neutral>",
  "recommendation": "<one sentence mediator action>"
}}
Text: {text}
""")
```

#### UI
- **Emotional Temperature Gauge**: Plotly indicator gauge. 0–30 = sage green (calm), 31–60 = amber (elevated), 61–100 = deep red (critical).
- **Cooling-off alert**: If temperature > 70, a pulsing terracotta banner reads: *"⚠️ Party appears highly emotional. Recommend 10-minute cooling-off period before proceeding."*
- **Emotion timeline**: Line chart showing temperature over negotiation turns.
- **Mediator recommendation** shown in a styled callout box below the gauge.
- Score saved to `cases.emotional_temp`.

---

### Feature 5 — Jurisdiction & Triviality Auto-Filter

**Page:** `pages/05_auto_filter.py`

#### What it does
A rule-based + LLM hybrid that runs before DLS scoring. Checks five conditions in sequence and short-circuits on first failure. If all pass, the case proceeds. Results stored in `cases.filter_result`.

#### Filter Pipeline

```python
# Pure rule-based checks first (fast), then LLM for ambiguous cases

def run_filter(case: dict) -> dict:
    checks = []

    # 1. Small claims threshold
    if case["claim_amount"] < 500:
        return fail("Claim below $500 minimum. Route to small claims.", "small_claims_reroute")

    # 2. Government defendant routing
    if "government" in case["defendant_type"]:
        return fail("Government party detected. Must file via administrative tribunal.", "admin_route")

    # 3. Deduplication — check SQLite for matching (plaintiff, defendant, category) combo
    duplicate = db.check_duplicate(case["plaintiff_id"], case["defendant_id"], case["category"])
    if duplicate:
        return fail(f"Duplicate of case {duplicate['id']} already on file.", "duplicate")

    # 4. LLM jurisdiction check
    jurisdiction_ok = llm_check_jurisdiction(case)
    if not jurisdiction_ok["valid"]:
        return fail(jurisdiction_ok["reason"], "wrong_jurisdiction")

    # 5. Triviality check via LLM
    triviality = llm_check_triviality(case)
    if triviality["is_trivial"]:
        return fail(triviality["reason"], "trivial")

    return {"passed": True, "checks": checks, "routing": "standard"}
```

#### UI
- **Animated checklist**: Five rows, each with a spinner → green checkmark or red X as checks run sequentially (0.3s artificial delay per step for drama).
- **Result card**: Green (passed all) or terracotta (blocked) full-width card showing what failed and why, with the recommended routing action.
- **Stats strip** at bottom: "Estimated court time saved this session: X hours" calculated from number of filtered cases × 2 hours average.

---

### Feature 6 — Judge Cockpit

**Page:** `pages/06_judge_cockpit.py`

#### What it does
A single-screen read-only dashboard for escalated cases. Aggregates all signals from the pipeline into one compact view. A judge can review a full case in under 90 seconds. Styled as a high-contrast dark-mode interface within the warm Streamlit app (using dark card components on the cream background).

#### UI Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  CASE #XYZ · Landlord-Tenant Dispute · Filed 2024-01-15         │
├──────────┬──────────┬──────────────────────┬────────────────────┤
│ DLS SCORE│EMOTIONAL │  CASE DNA TWIN        │ AI RECOMMENDATION  │
│  [gauge] │  TEMP    │  Case #ABC (87% match)│  Rule for plaintiff│
│   72/100 │  [gauge] │  "Awarded $8,400"    │  Confidence: 81%   │
│          │  45/100  │                      │                    │
├──────────┴──────────┴──────────────────────┴────────────────────┤
│  NEGOTIATION SUMMARY                                             │
│  6 turns · Final offer: $7,200 · Defendant rejected             │
├─────────────────────────────────────────────────────────────────┤
│  STATUTE CITATIONS (AI-generated)                               │
│  • Civil Code §1942 — Habitability                              │
│  • Local Ordinance 47.3 — Notice requirements                   │
├─────────────────────────────────────────────────────────────────┤
│  ESTIMATED TIME TO RESOLVE: 3–6 weeks         [ESCALATE] [DISMISS]│
└─────────────────────────────────────────────────────────────────┘
```

#### Implementation Notes
- Statute citations generated by a LangChain chain: given case category + summary, Groq outputs 2–4 relevant statute references.
- Estimated time generated by simple rule mapping: `{category} × {dls_score_bucket} → weeks_range`.
- `[ESCALATE]` button updates `cases.status = 'escalated'`. `[DISMISS]` updates to `'dismissed'` with a reason input.
- All data pulled from SQLite — no live LLM calls on this page (everything pre-computed).

---

### Feature 7 — Quantum Conflict Graph

**Page:** `pages/07_conflict_graph.py` + `graph/conflict_graph.py`

#### What it does
Builds a NetworkX `MultiDiGraph` from `entities` and `case_edges`. When a new case is filed, the graph is traversed to surface the full conflict history of both parties. Node size = degree centrality. Rendered as an interactive Plotly network scatter plot.

#### Implementation

```python
# graph/conflict_graph.py
import networkx as nx
import sqlite3, json

def build_graph(db_path: str) -> nx.MultiDiGraph:
    G = nx.MultiDiGraph()
    conn = sqlite3.connect(db_path)
    
    for row in conn.execute("SELECT id, name, type FROM entities"):
        G.add_node(row[0], label=row[1], entity_type=row[2], case_count=0)
    
    for row in conn.execute("SELECT case_id, entity_a, entity_b, edge_type FROM case_edges"):
        G.add_edge(row[1], row[2], case_id=row[0], edge_type=row[3])
        G.nodes[row[1]]["case_count"] = G.nodes[row[1]].get("case_count", 0) + 1
        G.nodes[row[2]]["case_count"] = G.nodes[row[2]].get("case_count", 0) + 1
    
    conn.close()
    return G

def detect_repeat_offenders(G: nx.MultiDiGraph, threshold: int = 5) -> list[dict]:
    return [
        {"entity": n, "label": G.nodes[n]["label"], "case_count": G.nodes[n]["case_count"]}
        for n in G.nodes
        if G.nodes[n].get("case_count", 0) >= threshold
    ]

def get_entity_history(G: nx.MultiDiGraph, entity_id: str) -> dict:
    neighbors = list(G.neighbors(entity_id)) + list(G.predecessors(entity_id))
    subgraph = G.subgraph([entity_id] + neighbors)
    return {
        "node_count": subgraph.number_of_nodes(),
        "edge_count": subgraph.number_of_edges(),
        "subgraph": subgraph
    }
```

#### Plotly Network Visualization

```python
# utils/charts.py
import plotly.graph_objects as go
import networkx as nx

def render_conflict_graph(G: nx.MultiDiGraph):
    pos = nx.spring_layout(G, seed=42, k=2)
    centrality = nx.degree_centrality(G)
    
    edge_x, edge_y = [], []
    for u, v in G.edges():
        x0,y0 = pos[u]; x1,y1 = pos[v]
        edge_x += [x0,x1,None]; edge_y += [y0,y1,None]

    node_x = [pos[n][0] for n in G.nodes()]
    node_y = [pos[n][1] for n in G.nodes()]
    node_size = [10 + centrality[n]*60 for n in G.nodes()]
    node_color = ["#C0522B" if G.nodes[n].get("case_count",0)>5 else "#8B5E3C" for n in G.nodes()]
    node_text = [f"{G.nodes[n]['label']}<br>Cases: {G.nodes[n].get('case_count',0)}" for n in G.nodes()]

    fig = go.Figure(
        data=[
            go.Scatter(x=edge_x, y=edge_y, mode="lines",
                       line=dict(width=1, color="#A0522D"), hoverinfo="none"),
            go.Scatter(x=node_x, y=node_y, mode="markers+text",
                       marker=dict(size=node_size, color=node_color, line=dict(width=2, color="#F5F0E8")),
                       text=[G.nodes[n]["label"] for n in G.nodes()],
                       hovertext=node_text, hoverinfo="text",
                       textfont=dict(color="#2C1A0E", size=10))
        ],
        layout=go.Layout(
            paper_bgcolor="#F5F0E8", plot_bgcolor="#F5F0E8",
            showlegend=False, margin=dict(l=0,r=0,t=0,b=0),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
    )
    return fig
```

#### UI
- Full-width Plotly graph with zoom, pan, hover tooltips.
- **Repeat Offenders panel** (right sidebar): ranked list of entities with highest case counts, highlighted in deep terracotta.
- **Entity Inspector**: click a node → side panel shows full dispute history, all connected cases, timeline.
- **Pattern alerts**: if one entity has >5 cases of the same type against different parties, a banner reads *"⚠️ Potential systematic filing pattern detected."*

---

## 5. Shared Infrastructure

### Theme Injection

```python
# utils/theme.py
def inject_css():
    st.markdown("""
    <style>
    :root {
        --primary: #C0522B;
        --secondary: #8B5E3C;
        --bg: #F5F0E8;
        --surface: #EDE3D4;
        --text: #2C1A0E;
    }
    .stApp { background-color: var(--bg); }
    .stButton > button {
        background-color: var(--primary);
        color: white;
        border-radius: 6px;
        border: none;
        font-weight: 600;
    }
    .stButton > button:hover { background-color: #A0422B; }
    [data-testid="stSidebar"] { background-color: #8B5E3C; }
    [data-testid="stSidebar"] * { color: #F5F0E8 !important; }
    .metric-card {
        background: var(--surface);
        border-left: 4px solid var(--primary);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .warning-banner {
        background: #C0522B;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
```

### Groq LLM Setup

```python
# config.py
from langchain_groq import ChatGroq
import os

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = "llama3-70b-8192"   # or mixtral-8x7b-32768

def get_llm():
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=GROQ_MODEL,
        temperature=0.2,
        max_tokens=1024
    )
```

### `requirements.txt`

```
streamlit>=1.35.0
langchain>=0.2.0
langchain-groq>=0.1.0
langgraph>=0.1.0
networkx>=3.3
plotly>=5.22.0
textblob>=0.18.0
python-dotenv>=1.0.0
```

> All packages available on PyPI. Zero external services beyond Groq API (free tier sufficient for demo).

---

## 6. 7-Day Implementation Timeline

| Day | Focus | Deliverables |
|---|---|---|
| **Day 1** | Foundation | `schema.sql`, `database.py`, `config.py`, `theme.py`, `seed_data.py`, `app.py` nav shell, Groq connection test |
| **Day 2** | Case Filing + DNA | `01_file_case.py`, `dna_agent.py`, cosine similarity search, DNA helix Plotly chart |
| **Day 3** | DLS Engine + Filter | `dls_agent.py`, `02_dls_engine.py` gauge UI, `05_auto_filter.py` animated checklist |
| **Day 4** | Negotiation Sandbox | `negotiation_graph.py` (LangGraph), `03_negotiation.py` streaming chat UI, settlement generator |
| **Day 5** | Emotion Layer + Cockpit | `emotion_agent.py`, `04_emotion_monitor.py` gauge + timeline, `06_judge_cockpit.py` full layout |
| **Day 6** | Conflict Graph | `conflict_graph.py` (NetworkX), `07_conflict_graph.py` Plotly network, repeat offender detection |
| **Day 7** | Polish + Demo Prep | Seed realistic demo data, connect all pages end-to-end, CSS polish, README, rehearse demo flow |

---

## 7. Demo Flow (Hackathon Presentation)

1. **File a case** (landlord-tenant, $12,000 claim) → watch DNA vector compute → Case Twin appears.
2. **DLS Engine** lights up at 68 (amber) — show gauge drama, breakdown bars.
3. **Auto-Filter** runs animated checklist → all green → case proceeds.
4. **Negotiation Sandbox** — hit "Start AI Negotiation" → watch agents debate in real time → settlement at $9,500 in 7 turns.
5. **Emotion Monitor** — show plaintiff temperature spiking to 72 → cooling-off alert triggers.
6. **Judge Cockpit** — single-screen 90-second review, AI recommends ruling for plaintiff at 81% confidence.
7. **Conflict Graph** — reveal the defendant landlord as a hub with 23 prior complaints — audience gasps.

---

## 8. Key Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Groq rate limits during live demo | Pre-cache LLM responses for demo cases in SQLite; only call live for new input |
| LangGraph negotiation loops infinitely | Hard cap at `max_turns=10`; mediator forces convergence at turn 8 |
| NetworkX graph too dense to render | Cap visualization at 50 nodes; use subgraph around selected entity |
| Streamlit state loss on page switch | Store all case state in `st.session_state` and persist to SQLite on each action |
| LLM returns invalid JSON | Wrap all LLM calls in `try/except`; use `OutputFixingParser` from LangChain as fallback |

---

*Document version 1.0 · JusticeFlow Hackathon Build · 2025*
