import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test 1: DB init
from db.database import init_db, get_connection
init_db()
conn = get_connection()
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tables:", [t[0] for t in tables])
conn.close()
print("DB init OK")

# Test 2: Module imports
from config import get_llm, COLORS, CASE_CATEGORIES
print("Config OK:", COLORS["primary"], len(CASE_CATEGORIES), "categories")

from agents.dna_agent import build_dna_vector, cosine_similarity, find_case_twin
print("DNA agent OK")

from agents.dls_agent import compute_dls
print("DLS agent OK")

from agents.emotion_agent import analyze_emotion
print("Emotion agent OK")

from agents.negotiation_graph import run_negotiation
print("Negotiation agent OK")

from graph.conflict_graph import build_graph, detect_repeat_offenders
print("Conflict graph OK")

from utils.charts import render_gauge, render_dna_helix, render_conflict_graph
print("Charts OK")

from utils.theme import inject_css
print("Theme OK")

# Test 3: Seed data
from utils.seed_data import seed_all
cases, entities, edges = seed_all()
print(f"Seeded: {cases} cases, {entities} entities, {edges} edges")

# Test 4: Verify historical cases
from db.database import get_historical_cases
hist = get_historical_cases()
print(f"Historical cases in DB: {len(hist)}")

print("\n=== ALL TESTS PASSED ===")
