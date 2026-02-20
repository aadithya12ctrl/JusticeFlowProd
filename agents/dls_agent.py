# agents/dls_agent.py — AI Dismissal Probability Engine
import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


DLS_PROMPT = PromptTemplate.from_template("""
You are a senior court clerk. Analyze this case and estimate dismissal probability.
Return JSON only, no markdown, no explanation. Schema:
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
Claim amount: ${claim_amount}
Category: {category}
""")


def compute_dls(case: dict, llm) -> dict:
    chain = DLS_PROMPT | llm | StrOutputParser()
    try:
        raw = chain.invoke({
            "title": case.get("title", ""),
            "description": case.get("description", ""),
            "jurisdiction": case.get("jurisdiction", "Unknown"),
            "claim_amount": case.get("claim_amount", 0),
            "category": case.get("category", "other"),
        })
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"): raw = raw[:-3]
            raw = raw.strip()
        data = json.loads(raw)
        dls = max(0, min(100, int(data.get("dls", 50))))
        reasons = data.get("reasons", {})
        for key in ["lack_of_jurisdiction", "statute_of_limitations",
                     "insufficient_evidence", "frivolous_claim", "procedural_defect"]:
            reasons[key] = max(0, min(100, int(reasons.get(key, 0))))
        return {"dls": dls, "reasons": reasons, "explanation": data.get("explanation", "Analysis could not be completed.")}
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        return {
            "dls": 50,
            "reasons": {"lack_of_jurisdiction":10,"statute_of_limitations":10,"insufficient_evidence":10,"frivolous_claim":10,"procedural_defect":10},
            "explanation": f"Unable to fully analyze case. Default assessment applied. ({str(e)[:50]})",
        }
