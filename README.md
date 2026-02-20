# ⚖️ JusticeFlow — AI-Powered Dispute Resolution Platform

> **Reducing court backlogs through intelligent case analysis, autonomous negotiation, and data-driven judicial decision support.**

---

## 🎯 The Problem

Courts worldwide face a crisis: **millions of cases backlogged**, overburdened judges, and litigants waiting years for resolution. Most disputes — landlord-tenant conflicts, small claims, employment issues — follow predictable patterns, yet each is processed from scratch with no institutional memory.

**JusticeFlow** uses AI to solve this by:
- Auto-screening trivial and misrouted cases before they reach a judge
- Finding historical precedents through Case DNA Fingerprinting
- Running autonomous pre-trial negotiations between AI agents
- Giving judges a 90-second overview dashboard with AI-generated recommendations

---

## 👥 Who Is This For?

| Role | How JusticeFlow Helps |
|---|---|
| **Judges** | 90-second case review via the Judge Cockpit with AI recommendations, statute citations, and emotional temperature readings |
| **Legal Representatives** | Pre-trial negotiation sandbox where AI agents argue both sides, with the attorney presiding as judge to test strategies |
| **Court Administrators** | Auto-filter pipeline screens out trivial, duplicate, and misrouted cases — saving estimated 2 hours per case |
| **Litigants** | Faster resolution through AI-mediated settlement, reducing time-to-resolution from months to days |

---

## 🚀 Core Features

### 1. 📝 Case Filing + DNA Fingerprinting
Submit disputes through a structured form. The AI extracts a **6-dimensional Case DNA vector** — encoding category, jurisdiction clarity, claim size, evidence strength, emotional intensity, and novelty. This vector is compared against historical cases using **cosine similarity** to find a "Case Twin" — a past case with a similar profile and known outcome.

### 2. 📊 Dismissal Likelihood Score (DLS) Engine
An AI-powered risk gauge that estimates the probability of a case being dismissed. Breaks down risk across 5 dimensions: jurisdiction issues, statute of limitations, insufficient evidence, frivolous claims, and procedural defects. Cases scoring above 75% trigger a **warning banner** requiring judicial override to proceed.

### 3. 🤝 Interactive Negotiation Sandbox
Two AI agents with distinct system prompts — **Plaintiff Advocate** and **Defendant Advocate** — debate the case round by round. The human user presides as the **Judge**, injecting directions, observations, and questions between rounds. Both agents must acknowledge and respond to the judge's remarks. Supports forced settlement, escalation to trial, and downloadable settlement agreements.

### 4. 💭 Emotional Intelligence Monitor
Analyzes the emotional temperature (0–100) of case filings and negotiation transcripts. Detects dominant emotions (anger, fear, grief, frustration, neutral) and triggers **cooling-off period alerts** when temperature exceeds 70. Includes an emotion timeline chart across negotiation rounds.

### 5. 🔍 Auto-Filter Pipeline
A 5-step screening pipeline that runs sequentially with animated progress:
1. **Minimum Claim Threshold** — blocks cases under $500
2. **Government Party Detection** — routes to administrative tribunal
3. **Duplicate Case Check** — flags existing active cases
4. **AI Jurisdiction Validation** — LLM-powered court routing check
5. **AI Triviality Assessment** — screens out frivolous claims

Short-circuits on first failure with routing recommendations.

### 6. 👨‍⚖️ Judge Cockpit
A unified dashboard for judicial review, aggregating all AI signals into a single view:
- DLS score, emotional temperature, Case DNA twin match, AI recommendation
- Negotiation summary with turn count and settlement status
- AI-generated statute citations with relevance explanations
- Estimated time to resolution by case category
- One-click Escalate / Dismiss actions

### 7. 🕸️ Conflict Graph
A **NetworkX-powered graph** visualizing the dispute network — entities (people, companies, government bodies) as nodes, disputes as edges. Detects **repeat offenders** (entities involved in 3+ cases) and **systematic filing patterns** (e.g., a landlord sued by 5 different tenants).

---

## 🛠️ Tech Stack

| Technology | Purpose | Why It's Necessary |
|---|---|---|
| **Python 3.12** | Core language | Industry standard for AI/ML applications |
| **Streamlit** | Web UI framework | Rapid prototyping of data-driven dashboards with zero frontend code |
| **Groq + LLaMA 3.3 70B** | LLM inference | Ultra-fast inference (< 1s latency) for real-time legal analysis |
| **LangChain** | LLM orchestration | Structured prompting with `PromptTemplate` → LLM → `StrOutputParser` pipeline (LCEL pattern) |
| **SQLite** | Database | Zero-config embedded database — no server setup needed for local deployment |
| **NetworkX** | Graph engine | In-memory graph construction for conflict network analysis and repeat offender detection |
| **Plotly** | Visualizations | Interactive charts: gauge meters, radar comparisons, network graphs, emotion timelines |
| **TextBlob / NLTK** | NLP utilities | Lightweight sentiment analysis fallback when LLM is unavailable |

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Streamlit UI (app.py)               │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│   │ File Case│ │DLS Engine│ │Negotiaton│  ... 7 pgs │
│   └────┬─────┘ └────┬─────┘ └────┬─────┘           │
├────────┼────────────┼────────────┼───────────────────┤
│        ▼            ▼            ▼                   │
│   ┌──────────────────────────────────────────┐      │
│   │          AI Agents (LangChain + Groq)     │      │
│   │  dna_agent │ dls_agent │ emotion_agent    │      │
│   │           negotiation_graph               │      │
│   └──────────────────┬───────────────────────┘      │
│                      ▼                               │
│   ┌─────────────┐  ┌─────────────────┐              │
│   │  SQLite DB  │  │ NetworkX Graph  │              │
│   │ (5 tables)  │  │ (conflict net)  │              │
│   └─────────────┘  └─────────────────┘              │
└─────────────────────────────────────────────────────┘
```

---

## 📦 Project Structure

```
JusticeFlowProd/
├── app.py                     # Main entry point + sidebar navigation
├── config.py                  # LLM factory, color tokens, DB path
├── requirements.txt           # Python dependencies
├── agents/
│   ├── dna_agent.py           # Case DNA fingerprinting + cosine similarity
│   ├── dls_agent.py           # Dismissal Likelihood Score engine
│   ├── emotion_agent.py       # Emotional temperature analysis
│   └── negotiation_graph.py   # Multi-agent negotiation with judge intervention
├── db/
│   ├── schema.sql             # SQLite table definitions (5 tables)
│   └── database.py            # Connection management + CRUD helpers
├── graph/
│   └── conflict_graph.py      # NetworkX graph builder + pattern detection
├── pages/
│   ├── page_01_file_case.py   # Case submission + DNA visualization
│   ├── page_02_dls_engine.py  # Dismissal gauge + reason breakdown
│   ├── page_03_negotiation.py # Interactive negotiation sandbox
│   ├── page_04_emotion_monitor.py
│   ├── page_05_auto_filter.py # 5-step screening pipeline
│   ├── page_06_judge_cockpit.py
│   └── page_07_conflict_graph.py
└── utils/
    ├── theme.py               # CSS design system (terracotta palette)
    ├── charts.py              # Plotly visualization helpers
    └── seed_data.py           # Demo data populator
```

---

## 🏃 Getting Started

### Prerequisites
- Python 3.10+
- A [Groq API key](https://console.groq.com/) (free tier available)

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
GROQ_API_KEY="your_key_here" streamlit run app.py
```

### Windows (PowerShell)
```powershell
$env:GROQ_API_KEY = "your_key_here"; streamlit run app.py
```

### First Run
1. Click **🌱 Seed Demo Data** in the sidebar to populate 12 historical cases
2. Navigate to **📝 File Case** and submit a dispute
3. Explore each feature page in order for the full demo flow

---

## 📄 License

This project is for educational and demonstration purposes.
