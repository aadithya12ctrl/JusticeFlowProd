# agents/dls_agent.py — AI Dismissal Probability Engine (v2)
# Enhanced with Indian statute citations, severity grades, precedent matching,
# weighted composite scoring, and per-reason recommendations.
import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


# ─── Indian Law Reference Weights ────────────────────────────────────
# Category-specific dismissal risk adjustments
CATEGORY_RISK_MODIFIERS = {
    "rera":               {"base_weight": 0.8, "key_statute": "RERA Act, 2016 §18 / CPA 2019"},
    "consumer":           {"base_weight": 0.7, "key_statute": "Consumer Protection Act, 2019 §35"},
    "motor_accident":     {"base_weight": 0.6, "key_statute": "Motor Vehicles Act, 1988 §166"},
    "rent_control":       {"base_weight": 0.7, "key_statute": "State Rent Control Acts / Transfer of Property Act"},
    "labour_industrial":  {"base_weight": 0.7, "key_statute": "Industrial Disputes Act, 1947 / POSH Act, 2013"},
    "family_matrimonial": {"base_weight": 0.6, "key_statute": "Hindu Marriage Act / CrPC §125"},
    "contract_civil":     {"base_weight": 0.8, "key_statute": "Indian Contract Act, 1872 §73"},
    "cheque_bounce":      {"base_weight": 0.9, "key_statute": "Negotiable Instruments Act, 1881 §138"},
}

# Claim amount risk thresholds (₹)
CLAIM_RISK = {
    "trivial": 25_000,      # Below this → high frivolous risk
    "small":   5_00_000,    # Consumer forum jurisdiction
    "medium":  50_00_000,   # District court
    "large":   200_00_000,  # High court territory
}


DLS_PROMPT = PromptTemplate.from_template("""You are a senior Indian court registrar with 25 years experience in case screening.
Analyze this case for dismissal probability under multiple Indian law frameworks.

EVALUATION FRAMEWORK:
1. JURISDICTION CHECK — CPC §9-11, specific tribunal vs. civil court jurisdiction.
   Is the case filed in the correct court/forum? (District Court vs. NCDRC vs. RERA Authority vs. MACT vs. Labour Court)
   Consider: pecuniary jurisdiction limits (₹1Cr for District Consumer Forum, ₹10Cr for State Commission)

2. LIMITATION PERIOD — Limitation Act, 1963
   RERA complaints: 1 year from possession date
   Consumer complaints: 2 years from cause of action
   Motor accident: 6 months (extendable by MACT)
   Cheque bounce (NI Act §138): 30 days from dishonour notice
   Contract disputes: 3 years
   Rent disputes: varies by state Rent Act

3. EVIDENCE SUFFICIENCY — Indian Evidence Act, 1872 §§101-106
   Does the description mention documentary evidence, witness statements, or digital records?
   Burden of proof analysis under §101.

4. LEGAL MERIT — CPC Order VII Rule 11(a)(d)
   Does the plaint disclose a cause of action?
   Is the claim barred by law?
   Are the relief sought and facts consistent?

5. PROCEDURAL COMPLIANCE — CPC Order VI Rule 15, Order VII Rule 1
   Proper verification of plaint? Correct court fees? Required parties joined?

6. STATUTE-SPECIFIC GROUNDS — {key_statute}
   Category-specific dismissal risks for {category} cases.

7. SETTLEMENT VIABILITY — What percentage of similar cases settle pre-trial?
   Based on the claim amount (₹{claim_amount}) and category history.

Return ONLY valid JSON (no markdown, no explanation outside JSON):
{{
  "dls": <int 0-100, weighted overall dismissal probability>,
  "confidence": <int 0-100, how confident you are in this assessment>,
  "severity": "<critical|high|moderate|low|minimal>",
  "reasons": {{
    "jurisdiction_defect": {{
      "score": <int 0-100>,
      "detail": "<one line explaining the specific jurisdiction issue or why it's clear>",
      "statute": "<specific statute section, e.g. CPC §9>"
    }},
    "limitation_expired": {{
      "score": <int 0-100>,
      "detail": "<one line on whether filing is within limitation>",
      "statute": "<e.g. Limitation Act §3, specific article>"
    }},
    "evidence_gap": {{
      "score": <int 0-100>,
      "detail": "<one line on evidence strength or weakness>",
      "statute": "<e.g. Indian Evidence Act §101>"
    }},
    "no_cause_of_action": {{
      "score": <int 0-100>,
      "detail": "<one line on whether plaint discloses valid cause of action>",
      "statute": "<e.g. CPC Order VII Rule 11(a)>"
    }},
    "procedural_defect": {{
      "score": <int 0-100>,
      "detail": "<one line on any procedural issues>",
      "statute": "<e.g. CPC Order VI Rule 15>"
    }}
  }},
  "applicable_precedents": [
    "<1 most relevant case name, e.g. Pioneer Urban Land vs Govindan Raghavan (2019)>"
  ],
  "recommendation": "<file|review_required|dismiss_likely|settlement_advised>",
  "explanation": "<3-4 sentence analysis citing specific Indian statutes and explaining the overall risk>"
}}

Case title: {title}
Category: {category}
Description: {description}
Jurisdiction: {jurisdiction}
Claim amount: ₹{claim_amount}
Plaintiff: {plaintiff}
Defendant: {defendant}
""")


def compute_dls(case: dict, llm) -> dict:
    """Enhanced DLS computation with category-specific modifiers and structured output."""
    category = case.get("category", "other")
    cat_info = CATEGORY_RISK_MODIFIERS.get(category, {"base_weight": 0.75, "key_statute": "CPC"})

    chain = DLS_PROMPT | llm | StrOutputParser()
    try:
        raw = chain.invoke({
            "title": case.get("title", ""),
            "description": case.get("description", ""),
            "jurisdiction": case.get("jurisdiction", "Unknown"),
            "claim_amount": case.get("claim_amount", 0),
            "category": category.replace("_", " ").title(),
            "plaintiff": case.get("plaintiff_name", "Unknown"),
            "defendant": case.get("defendant_name", "Unknown"),
            "key_statute": cat_info["key_statute"],
        })
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"): raw = raw[:-3]
            raw = raw.strip()
        data = json.loads(raw)

        # ── Extract & validate DLS score ──
        dls = max(0, min(100, int(data.get("dls", 50))))
        confidence = max(0, min(100, int(data.get("confidence", 60))))
        severity = data.get("severity", "moderate")
        if severity not in ("critical", "high", "moderate", "low", "minimal"):
            severity = "moderate"

        # ── Apply category-specific modifiers ──
        claim_amount = float(case.get("claim_amount", 0))
        # Trivial claim boost (below ₹25K → add 10 to frivolous score)
        trivial_boost = 0
        if claim_amount < CLAIM_RISK["trivial"] and claim_amount > 0:
            trivial_boost = 10

        # ── Extract per-reason structured data ──
        raw_reasons = data.get("reasons", {})
        reasons = {}
        reason_keys = ["jurisdiction_defect", "limitation_expired", "evidence_gap",
                       "no_cause_of_action", "procedural_defect"]
        for key in reason_keys:
            entry = raw_reasons.get(key, {})
            if isinstance(entry, dict):
                score = max(0, min(100, int(entry.get("score", 0))))
                if key == "no_cause_of_action":
                    score = min(100, score + trivial_boost)
                reasons[key] = {
                    "score": score,
                    "detail": str(entry.get("detail", "Not assessed")),
                    "statute": str(entry.get("statute", "N/A")),
                }
            else:
                # Backward compat: if LLM returns flat int
                score = max(0, min(100, int(entry))) if isinstance(entry, (int, float)) else 0
                reasons[key] = {"score": score, "detail": "Not assessed", "statute": "N/A"}

        # ── Weighted composite score (cross-check LLM output) ──
        weights = {
            "jurisdiction_defect": 0.25,
            "limitation_expired": 0.20,
            "evidence_gap": 0.20,
            "no_cause_of_action": 0.25,
            "procedural_defect": 0.10,
        }
        weighted_dls = sum(reasons[k]["score"] * weights[k] for k in reason_keys)
        # Blend LLM's raw DLS with our weighted calc (70% LLM, 30% computed)
        final_dls = int(0.7 * dls + 0.3 * weighted_dls)
        final_dls = max(0, min(100, final_dls))

        # ── Recalculate severity from final score ──
        if final_dls >= 80: severity = "critical"
        elif final_dls >= 60: severity = "high"
        elif final_dls >= 40: severity = "moderate"
        elif final_dls >= 20: severity = "low"
        else: severity = "minimal"

        # ── Precedents ──
        precedents = data.get("applicable_precedents", [])
        if not isinstance(precedents, list):
            precedents = [str(precedents)]
        precedents = [str(p) for p in precedents[:3]]

        recommendation = data.get("recommendation", "review_required")
        explanation = data.get("explanation", "Analysis could not be completed.")

        return {
            "dls": final_dls,
            "confidence": confidence,
            "severity": severity,
            "reasons": reasons,
            "precedents": precedents,
            "recommendation": recommendation,
            "explanation": explanation,
            # Flat reasons for backward compatibility with DB storage
            "reasons_flat": {k: reasons[k]["score"] for k in reason_keys},
        }
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        return {
            "dls": 50,
            "confidence": 30,
            "severity": "moderate",
            "reasons": {k: {"score": 10, "detail": "Unable to assess", "statute": "N/A"}
                        for k in ["jurisdiction_defect", "limitation_expired", "evidence_gap",
                                  "no_cause_of_action", "procedural_defect"]},
            "precedents": [],
            "recommendation": "review_required",
            "explanation": f"Unable to fully analyze case. Default assessment applied. ({str(e)[:80]})",
            "reasons_flat": {k: 10 for k in ["jurisdiction_defect", "limitation_expired",
                                              "evidence_gap", "no_cause_of_action", "procedural_defect"]},
        }
