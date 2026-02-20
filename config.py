# config.py — Constants, DB path, Groq API key setup
import os

# ─── Paths ────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "justiceflow.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "db", "schema.sql")

# ─── Groq LLM ────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"

# ─── Design Tokens ───────────────────────────────────────────────────
COLORS = {
    "primary":    "#C0522B",   # Terracotta Red
    "secondary":  "#8B5E3C",   # Warm Brown
    "background": "#F5F0E8",   # Cream
    "surface":    "#EDE3D4",   # Beige
    "accent":     "#A0522D",   # Sienna
    "text_dark":  "#2C1A0E",   # Dark Espresso
    "text_light": "#6B4C35",   # Mocha
    "success":    "#6B8F71",   # Sage Green
    "warning":    "#D4A843",   # Amber
    "danger":     "#B03A2E",   # Deep Red
}

# ─── Case Categories ─────────────────────────────────────────────────
CASE_CATEGORIES = [
    "landlord_tenant",
    "employment",
    "contract",
    "personal_injury",
    "family",
    "small_claims",
    "other",
]

# ─── LLM Factory ─────────────────────────────────────────────────────
def get_llm(temperature: float = 0.2, max_tokens: int = 1024):
    """Return a ChatGroq instance configured with the project defaults."""
    from langchain_groq import ChatGroq

    return ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=GROQ_MODEL,
        temperature=temperature,
        max_tokens=max_tokens,
    )
