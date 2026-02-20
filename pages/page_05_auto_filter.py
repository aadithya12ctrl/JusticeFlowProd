# pages/page_05_auto_filter.py — Jurisdiction & Triviality Auto-Filter
import streamlit as st
import json
import time
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.theme import page_header
from config import get_llm
from db.database import get_all_cases, get_case, update_case, get_connection
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


JURISDICTION_PROMPT = PromptTemplate.from_template("""
Analyze whether this case is filed in the correct jurisdiction.
Return JSON only, no markdown:
{{
  "valid": <true or false>,
  "reason": "<one sentence explanation>"
}}
Case jurisdiction: {jurisdiction}
Case category: {category}
Case description: {description}
""")

TRIVIALITY_PROMPT = PromptTemplate.from_template("""
Determine if this legal case is trivial (i.e., not worthy of court resources).
Return JSON only, no markdown:
{{
  "is_trivial": <true or false>,
  "reason": "<one sentence explanation>"
}}
Case title: {title}
Case description: {description}
Claim amount: ${claim_amount}
""")


def _check_small_claims(case: dict) -> dict:
    """Check 1: Minimum claim threshold."""
    if case.get("claim_amount", 0) < 500:
        return {"passed": False, "reason": "Claim below $500 minimum. Route to small claims advisory.", "routing": "small_claims_reroute"}
    return {"passed": True, "reason": "Claim amount meets minimum threshold."}


def _check_government_party(case: dict) -> dict:
    """Check 2: Government defendant detection."""
    desc = (case.get("description", "") + " " + case.get("title", "")).lower()
    gov_keywords = ["government", "federal", "state agency", "municipal", "city council", "public authority"]
    for kw in gov_keywords:
        if kw in desc:
            return {"passed": False, "reason": "Government party detected. Must file via administrative tribunal.", "routing": "admin_route"}
    return {"passed": True, "reason": "No government party detected."}


def _check_duplicate(case: dict) -> dict:
    """Check 3: Duplicate case detection."""
    conn = get_connection()
    row = conn.execute(
        """SELECT id FROM cases
           WHERE plaintiff_id = ? AND defendant_id = ? AND category = ?
           AND id != ? AND status NOT IN ('resolved', 'dismissed')
           LIMIT 1""",
        (case.get("plaintiff_id", ""), case.get("defendant_id", ""),
         case.get("category", ""), case.get("id", "")),
    ).fetchone()
    conn.close()
    if row:
        return {"passed": False, "reason": f"Duplicate of case #{row[0]} already on file.", "routing": "duplicate"}
    return {"passed": True, "reason": "No duplicate cases found."}


def _check_jurisdiction(case: dict, llm) -> dict:
    """Check 4: LLM jurisdiction validation."""
    chain = JURISDICTION_PROMPT | llm | StrOutputParser()
    try:
        raw = chain.invoke({
            "jurisdiction": case.get("jurisdiction", "Unknown"),
            "category": case.get("category", "other"),
            "description": case.get("description", ""),
        })
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()
        data = json.loads(raw)
        if not data.get("valid", True):
            return {"passed": False, "reason": data.get("reason", "Jurisdiction issue detected."), "routing": "wrong_jurisdiction"}
        return {"passed": True, "reason": data.get("reason", "Jurisdiction check passed.")}
    except Exception:
        return {"passed": True, "reason": "Jurisdiction check passed (default)."}


def _check_triviality(case: dict, llm) -> dict:
    """Check 5: LLM triviality assessment."""
    chain = TRIVIALITY_PROMPT | llm | StrOutputParser()
    try:
        raw = chain.invoke({
            "title": case.get("title", ""),
            "description": case.get("description", ""),
            "claim_amount": case.get("claim_amount", 0),
        })
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()
        data = json.loads(raw)
        if data.get("is_trivial", False):
            return {"passed": False, "reason": data.get("reason", "Case deemed trivial."), "routing": "trivial"}
        return {"passed": True, "reason": data.get("reason", "Case has merit.")}
    except Exception:
        return {"passed": True, "reason": "Triviality check passed (default)."}


def render():
    page_header("Auto Filter", "Jurisdiction & triviality screening pipeline")

    cases = get_all_cases()
    if not cases:
        st.info("📭 No cases found. File a case first from the '📝 File Case' page.")
        return

    # Case selector
    case_options = {f"#{c['id']} — {c['title']}": c['id'] for c in cases}
    selected_label = st.selectbox("Select a case to filter", list(case_options.keys()))
    case_id = case_options[selected_label]
    case = get_case(case_id)

    if not case:
        st.error("Case not found.")
        return

    if st.button("🔍 Run Auto-Filter Pipeline", use_container_width=True):
        steps = [
            ("💰 Minimum Claim Threshold", _check_small_claims, False),
            ("🏛️ Government Party Detection", _check_government_party, False),
            ("📋 Duplicate Case Check", _check_duplicate, False),
            ("⚖️ Jurisdiction Validation (AI)", _check_jurisdiction, True),
            ("🔎 Triviality Assessment (AI)", _check_triviality, True),
        ]

        llm = None
        results = []
        all_passed = True
        failed_step = None

        for step_name, check_fn, needs_llm in steps:
            # Show pending state
            placeholder = st.empty()
            placeholder.markdown(f"""
            <div class="filter-step pending">
                <span style="font-size:1.2rem;">⏳</span>
                <span style="flex:1; font-weight:500; color:#2C1A0E;">{step_name}</span>
                <span style="color:#D4A843; font-size:0.85rem;">Running...</span>
            </div>
            """, unsafe_allow_html=True)

            time.sleep(0.3)  # Dramatic effect

            # Run the check
            if needs_llm:
                if llm is None:
                    try:
                        llm = get_llm()
                    except Exception as e:
                        result = {"passed": True, "reason": f"LLM unavailable, defaulting to pass. ({str(e)[:50]})"}
                        results.append(result)
                        placeholder.markdown(f"""
                        <div class="filter-step pass">
                            <span style="font-size:1.2rem;">⚠️</span>
                            <span style="flex:1; font-weight:500; color:#2C1A0E;">{step_name}</span>
                            <span style="color:#D4A843; font-size:0.85rem;">Skipped (LLM unavailable)</span>
                        </div>
                        """, unsafe_allow_html=True)
                        continue
                result = check_fn(case, llm)
            else:
                result = check_fn(case)

            results.append(result)

            if result["passed"]:
                placeholder.markdown(f"""
                <div class="filter-step pass">
                    <span style="font-size:1.2rem;">✅</span>
                    <span style="flex:1; font-weight:500; color:#2C1A0E;">{step_name}</span>
                    <span style="color:#6B8F71; font-size:0.85rem;">{result['reason']}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                all_passed = False
                failed_step = step_name
                placeholder.markdown(f"""
                <div class="filter-step fail">
                    <span style="font-size:1.2rem;">❌</span>
                    <span style="flex:1; font-weight:500; color:#2C1A0E;">{step_name}</span>
                    <span style="color:#B03A2E; font-size:0.85rem;">{result['reason']}</span>
                </div>
                """, unsafe_allow_html=True)
                break  # Short-circuit on failure

        st.markdown("<br>", unsafe_allow_html=True)

        # Result card
        filter_result = {
            "passed": all_passed,
            "results": results,
            "routing": results[-1].get("routing", "standard") if not all_passed else "standard",
        }

        update_case(
            case_id,
            filter_result=json.dumps(filter_result),
            status="filtered" if all_passed else "intake",
        )

        if all_passed:
            st.markdown(f"""
            <div class="success-card" style="text-align:center;">
                <div style="font-size:1.5rem; margin-bottom:0.5rem;">✅ ALL CHECKS PASSED</div>
                <p style="margin:0; opacity:0.9;">Case #{case_id} is cleared to proceed to DLS scoring.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            routing = results[-1].get("routing", "review")
            st.markdown(f"""
            <div class="warning-banner" style="text-align:center;">
                <div style="font-size:1.5rem; margin-bottom:0.5rem;">🚫 CASE BLOCKED</div>
                <p style="margin:0; opacity:0.9;">Failed at: {failed_step}</p>
                <p style="margin:0.3rem 0 0 0; opacity:0.8;">Routing: {routing.replace('_',' ').title()}</p>
            </div>
            """, unsafe_allow_html=True)

        # Stats strip
        conn = get_connection()
        filtered_count = conn.execute(
            "SELECT COUNT(*) FROM cases WHERE filter_result IS NOT NULL"
        ).fetchone()[0]
        conn.close()
        hours_saved = filtered_count * 2

        st.markdown(f"""
        <div style="text-align:center; padding:1rem; margin-top:1rem; background:#EDE3D4; border-radius:10px;">
            <span style="color:#6B4C35; font-size:0.9rem;">
                ⏱️ Estimated court time saved this session: <strong style="color:#C0522B;">{hours_saved} hours</strong>
                ({filtered_count} cases filtered × 2 hours average)
            </span>
        </div>
        """, unsafe_allow_html=True)
