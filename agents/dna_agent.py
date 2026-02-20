# agents/dna_agent.py — Case DNA Fingerprinting via LangChain + Groq
import json
import math
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


DNA_PROMPT = PromptTemplate.from_template("""
You are a legal classification engine. Given this case description, extract a JSON object with these fields:
- category: one of [landlord_tenant, employment, contract, personal_injury, family, small_claims, other]
- jurisdiction_score: 0.0-1.0 (how clearly the correct court is stated)
- claim_bucket: 1=<$1k, 2=$1k-10k, 3=$10k-100k, 4=>$100k
- evidence_strength: 0.0-1.0
- emotional_intensity: 0.0-1.0
- novelty: 0.0-1.0 (how unusual the claim is)

Return ONLY valid JSON, no markdown, no explanation. Case: {case_text}
""")

CATEGORY_MAP = {
    "landlord_tenant": 0.1, "employment": 0.2, "contract": 0.3,
    "personal_injury": 0.4, "family": 0.5, "small_claims": 0.6, "other": 0.9,
}


def build_dna_vector(case_text: str, llm) -> list[float]:
    chain = DNA_PROMPT | llm | StrOutputParser()
    try:
        raw = chain.invoke({"case_text": case_text})
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"): raw = raw[:-3]
            raw = raw.strip()
        data = json.loads(raw)
        return [
            CATEGORY_MAP.get(data.get("category", "other"), 0.9),
            float(data.get("jurisdiction_score", 0.5)),
            float(data.get("claim_bucket", 2)) / 4.0,
            float(data.get("evidence_strength", 0.5)),
            float(data.get("emotional_intensity", 0.5)),
            float(data.get("novelty", 0.5)),
        ]
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return [0.5, 0.5, 0.5, 0.5, 0.5, 0.5]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x ** 2 for x in a))
    mag_b = math.sqrt(sum(x ** 2 for x in b))
    return dot / (mag_a * mag_b + 1e-9)


def find_case_twin(vector: list[float], historical_cases: list[dict]) -> tuple[dict | None, float]:
    best_match, best_score = None, -1.0
    for case in historical_cases:
        try:
            hv = json.loads(case["dna_vector"]) if isinstance(case["dna_vector"], str) else case["dna_vector"]
            score = cosine_similarity(vector, hv)
            if score > best_score:
                best_score, best_match = score, case
        except (json.JSONDecodeError, TypeError):
            continue
    return best_match, best_score
