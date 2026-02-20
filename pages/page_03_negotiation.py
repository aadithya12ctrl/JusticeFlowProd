# pages/page_03_negotiation.py — Interactive Negotiation Sandbox
# Two AI agents (Plaintiff Advocate + Defendant Advocate) debate round-by-round.
# The human user intervenes after each round as the presiding Judge.
import streamlit as st
import json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.theme import page_header
from config import get_llm
from db.database import (
    get_all_cases, get_case, update_case,
    insert_negotiation_turn, get_negotiation_log, get_entity_name,
)
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ─── Agent System Prompts ─────────────────────────────────────────────

PLAINTIFF_AGENT_PROMPT = PromptTemplate.from_template("""
SYSTEM: You are the Plaintiff's Legal Advocate AI. You ALWAYS argue in favor of the plaintiff.
Your job is to build the strongest possible case for why the plaintiff deserves the claimed amount.
Cite legal principles, precedents, and fairness arguments. Be persuasive but professional.
If the presiding judge has given directions or observations, you MUST acknowledge and respond to them.

CASE: {case_summary}
PLAINTIFF INTERESTS: {plaintiff_interests}
ORIGINAL CLAIM: ${claim_amount}
CURRENT OFFER ON TABLE: ${current_offer}
ROUND: {round} of {max_rounds}

FULL NEGOTIATION HISTORY:
{history}

{human_input}

Respond with JSON only, no markdown:
{{"message": "<your 2-4 sentence argument for this round, cite a specific legal principle or precedent>", "proposed_amount": <float — your proposed settlement amount>, "willing_to_settle": <true if you'd accept current offer, false otherwise>}}
""")

DEFENDANT_AGENT_PROMPT = PromptTemplate.from_template("""
SYSTEM: You are the Defendant's Legal Advocate AI. You ALWAYS argue in favor of the defendant.
Your job is to minimize the defendant's liability while appearing reasonable.
Cite legal defenses, challenge evidence, and propose lower settlements. Be strategic but fair.
If the presiding judge has given directions or observations, you MUST acknowledge and respond to them.

CASE: {case_summary}
DEFENDANT INTERESTS: {defendant_interests}
ORIGINAL CLAIM: ${claim_amount}
CURRENT OFFER ON TABLE: ${current_offer}
ROUND: {round} of {max_rounds}

FULL NEGOTIATION HISTORY:
{history}

{human_input}

Respond with JSON only, no markdown:
{{"message": "<your 2-4 sentence counter-argument, cite a legal defense or precedent>", "proposed_amount": <float — your proposed settlement amount>, "willing_to_settle": <true if you'd accept current offer, false otherwise>}}
""")


def _clean_json(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"): raw = raw[:-3]
    return raw.strip()


def _format_history(history: list[dict]) -> str:
    if not history:
        return "(No exchanges yet — this is the opening round.)"
    lines = []
    for h in history:
        role = h.get("role", "")
        icon = "👤" if "Plaintiff" in role else "👤" if "Defendant" in role else "🧑‍⚖️"
        lines.append(f"[{icon} {role}]: {h['message']} (Proposed: ${h.get('amount', 'N/A')})")
    return "\n".join(lines)


def _run_agent(prompt_template, params, llm):
    chain = prompt_template | llm | StrOutputParser()
    try:
        raw = chain.invoke(params)
        data = json.loads(_clean_json(raw))
        return {
            "message": data.get("message", "No response."),
            "amount": float(data.get("proposed_amount", params.get("current_offer", 0))),
            "willing": bool(data.get("willing_to_settle", False)),
        }
    except (json.JSONDecodeError, TypeError, ValueError):
        return {"message": "I maintain my current position and await further discussion.", "amount": params.get("current_offer", 0), "willing": False}


def render():
    page_header("Negotiation Sandbox", "Two AI agents debate — you preside as the Judge")

    cases = get_all_cases()
    if not cases:
        st.info("📭 No cases found. File a case first from the '📝 File Case' page.")
        return

    # Case selector
    case_options = {f"#{c['id']} — {c['title']}": c['id'] for c in cases}
    selected_label = st.selectbox("Select a case", list(case_options.keys()))
    case_id = case_options[selected_label]
    case = get_case(case_id)
    if not case:
        st.error("Case not found.")
        return

    # Initialize session state for this negotiation
    neg_key = f"neg_{case_id}"
    if neg_key not in st.session_state:
        st.session_state[neg_key] = {
            "history": [],
            "current_offer": case.get("claim_amount", 0),
            "round": 0,
            "status": "setup",  # setup | awaiting_human | running | settled | failed
            "max_rounds": 7,
            "plaintiff_interests": "",
            "defendant_interests": "",
        }
    neg = st.session_state[neg_key]

    # ─── SETUP PHASE ──────────────────────────────────────────────
    if neg["status"] == "setup":
        st.markdown("### 🎯 Configure Negotiation")
        col1, col2 = st.columns(2)
        with col1:
            p_name = get_entity_name(case.get("plaintiff_id", ""))
            neg["plaintiff_interests"] = st.text_area(
                f"👤 Plaintiff ({p_name}) Interests",
                value=f"Seeking full compensation of ${case.get('claim_amount', 0):,.2f} for all damages.",
                height=100, key=f"pi_{case_id}",
            )
        with col2:
            d_name = get_entity_name(case.get("defendant_id", ""))
            neg["defendant_interests"] = st.text_area(
                f"👤 Defendant ({d_name}) Interests",
                value="Disputing claimed amount. Willing to negotiate a fair settlement to avoid trial costs.",
                height=100, key=f"di_{case_id}",
            )
        neg["max_rounds"] = st.slider("Maximum Rounds", 3, 10, 7, key=f"mr_{case_id}")

        if st.button("🤝 Start Round-by-Round Negotiation", use_container_width=True):
            neg["status"] = "awaiting_human"
            neg["round"] = 1
            st.rerun()

    # ─── RENDER HISTORY ───────────────────────────────────────────
    if neg["history"]:
        st.markdown("---")
        st.markdown("### 💬 Negotiation Transcript")
        for entry in neg["history"]:
            role = entry.get("role", "")
            msg = entry.get("message", "")
            amt = entry.get("amount", 0)

            if "Plaintiff" in role:
                st.markdown(f"""
                <div class="chat-plaintiff">
                    <strong style="color:#A0522D;">👤 {role}</strong>
                    <span style="float:right; color:#C0522B; font-weight:700;">${amt:,.2f}</span>
                    <p style="color:#2C1A0E; margin:0.3rem 0 0 0;">{msg}</p>
                </div>
                """, unsafe_allow_html=True)
            elif "Defendant" in role:
                st.markdown(f"""
                <div class="chat-defendant">
                    <strong style="color:#8B5E3C;">👤 {role}</strong>
                    <span style="float:right; color:#8B5E3C; font-weight:700;">${amt:,.2f}</span>
                    <p style="color:#2C1A0E; margin:0.3rem 0 0 0;">{msg}</p>
                </div>
                """, unsafe_allow_html=True)
            elif "Judge" in role:
                st.markdown(f"""
                <div style="background:#D4A84333; border-left:4px solid #D4A843; border-radius:0 12px 12px 0; padding:1rem; margin:0.5rem 0;">
                    <strong style="color:#D4A843;">👨‍⚖️ {role}</strong>
                    <p style="color:#2C1A0E; margin:0.3rem 0 0 0;">{msg}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:#6B8F7122; border-left:4px solid #6B8F71; border-radius:0 12px 12px 0; padding:1rem; margin:0.5rem 0;">
                    <strong style="color:#6B8F71;">⚖️ {role}</strong>
                    <p style="color:#2C1A0E; margin:0.3rem 0 0 0;">{msg}</p>
                </div>
                """, unsafe_allow_html=True)

    # Current offer display
    if neg["status"] not in ("setup",):
        st.markdown(f"""
        <div style="text-align:center; padding:1rem; margin:1rem 0; background:linear-gradient(135deg,#2C1A0E,#3D2818); border-radius:12px;">
            <div style="color:#D4A843; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.1em;">Current Offer on Table</div>
            <div style="color:#F5F0E8; font-size:2.5rem; font-weight:800;">${neg['current_offer']:,.2f}</div>
            <div style="color:#F5F0E8; opacity:0.6; font-size:0.85rem;">Round {neg['round']} of {neg['max_rounds']}</div>
        </div>
        """, unsafe_allow_html=True)

    # ─── HUMAN INPUT PHASE ────────────────────────────────────────
    if neg["status"] == "awaiting_human":
        st.markdown(f"### 👨‍⚖️ Round {neg['round']} — Your Turn, Judge")
        st.markdown("""
        <div class="metric-card" style="border-left-color:#D4A843;">
            <p style="color:#2C1A0E; margin:0;">
                As the presiding judge, type your directions, observations, or questions below. Both AI agents will
                read your input and factor it into their next response. Leave blank to let the agents debate freely.
            </p>
        </div>
        """, unsafe_allow_html=True)

        human_input = st.text_area(
            "Judge's remarks (optional):",
            placeholder="e.g. 'The court notes the plaintiff has documented evidence. Defendant, address the repair timeline...'",
            height=100, key=f"human_{case_id}_{neg['round']}",
        )

        col_run, col_settle, col_end = st.columns([2, 1, 1])
        with col_run:
            run_round = st.button(f"▶️ Run Round {neg['round']}", use_container_width=True)
        with col_settle:
            force_settle = st.button("✅ Force Settlement", use_container_width=True)
        with col_end:
            end_neg = st.button("🛑 End Negotiation", use_container_width=True)

        if force_settle:
            neg["status"] = "settled"
            neg["history"].append({
                "role": "System",
                "message": f"Judge ordered settlement at ${neg['current_offer']:,.2f}.",
                "amount": neg["current_offer"],
            })
            update_case(case_id, status="resolved", settlement_text=f"Settled at ${neg['current_offer']:,.2f} by judicial order.")
            st.rerun()

        if end_neg:
            neg["status"] = "failed"
            neg["history"].append({
                "role": "System",
                "message": "Negotiation ended by the Judge. Case escalated to trial.",
                "amount": neg["current_offer"],
            })
            update_case(case_id, status="escalated")
            st.rerun()

        if run_round:
            # Record human input if provided
            if human_input and human_input.strip():
                neg["history"].append({
                    "role": "Presiding Judge",
                    "message": human_input.strip(),
                    "amount": neg["current_offer"],
                })
                human_context = f"THE PRESIDING JUDGE DIRECTS: {human_input.strip()}"
            else:
                human_context = ""

            case_summary = f"{case['title']}. {case['description']}"
            history_text = _format_history(neg["history"])

            with st.spinner(f"🤖 Round {neg['round']} — Plaintiff Agent is arguing..."):
                llm = get_llm(temperature=0.4, max_tokens=512)

                # Plaintiff argues
                p_result = _run_agent(PLAINTIFF_AGENT_PROMPT, {
                    "case_summary": case_summary,
                    "plaintiff_interests": neg["plaintiff_interests"],
                    "claim_amount": case.get("claim_amount", 0),
                    "current_offer": neg["current_offer"],
                    "round": neg["round"],
                    "max_rounds": neg["max_rounds"],
                    "history": history_text,
                    "human_input": human_context,
                }, llm)

                neg["history"].append({
                    "role": "Plaintiff Advocate AI",
                    "message": p_result["message"],
                    "amount": p_result["amount"],
                })
                neg["current_offer"] = p_result["amount"]

            with st.spinner(f"🤖 Round {neg['round']} — Defendant Agent is responding..."):
                # Update history for defendant
                history_text = _format_history(neg["history"])

                d_result = _run_agent(DEFENDANT_AGENT_PROMPT, {
                    "case_summary": case_summary,
                    "defendant_interests": neg["defendant_interests"],
                    "claim_amount": case.get("claim_amount", 0),
                    "current_offer": neg["current_offer"],
                    "round": neg["round"],
                    "max_rounds": neg["max_rounds"],
                    "history": history_text,
                    "human_input": human_context,
                }, llm)

                neg["history"].append({
                    "role": "Defendant Advocate AI",
                    "message": d_result["message"],
                    "amount": d_result["amount"],
                })
                neg["current_offer"] = d_result["amount"]

            # Save to DB
            insert_negotiation_turn(case_id, neg["round"], "human_mediator", human_input or "(no input)")
            insert_negotiation_turn(case_id, neg["round"], "agent_plaintiff", f"{p_result['message']} [${p_result['amount']:,.2f}]")
            insert_negotiation_turn(case_id, neg["round"], "agent_defendant", f"{d_result['message']} [${d_result['amount']:,.2f}]")

            # Check if both agents willing to settle
            if p_result["willing"] and d_result["willing"]:
                avg = (p_result["amount"] + d_result["amount"]) / 2
                neg["current_offer"] = avg
                neg["status"] = "settled"
                neg["history"].append({
                    "role": "System",
                    "message": f"Both agents agree to settle at ${avg:,.2f}!",
                    "amount": avg,
                })
                update_case(case_id, status="resolved", settlement_text=f"Settled at ${avg:,.2f}")
            elif neg["round"] >= neg["max_rounds"]:
                neg["status"] = "failed"
                neg["history"].append({
                    "role": "System",
                    "message": "Maximum rounds reached without agreement. Case escalated.",
                    "amount": neg["current_offer"],
                })
                update_case(case_id, status="escalated")
            else:
                neg["round"] += 1

            st.rerun()

    # ─── SETTLED / FAILED ─────────────────────────────────────────
    if neg["status"] == "settled":
        st.markdown(f"""
        <div class="success-card" style="text-align:center; font-size:1.2rem;">
            ✅ SETTLEMENT REACHED — ${neg['current_offer']:,.2f}
        </div>
        """, unsafe_allow_html=True)

        p_name = get_entity_name(case.get("plaintiff_id", ""))
        d_name = get_entity_name(case.get("defendant_id", ""))
        agreement = f"""SETTLEMENT AGREEMENT
====================
Case ID: #{case_id}  —  {case['title']}
Plaintiff: {p_name}  |  Defendant: {d_name}
Settlement Amount: ${neg['current_offer']:,.2f}
Original Claim:   ${case.get('claim_amount', 0):,.2f}
Rounds: {neg['round']}  |  Status: SETTLED
"""
        st.code(agreement, language="text")
        st.download_button("📥 Download Agreement", agreement, file_name=f"settlement_{case_id}.txt", mime="text/plain")

        if st.button("🔄 New Negotiation", key="reset"):
            del st.session_state[neg_key]
            st.rerun()

    elif neg["status"] == "failed":
        st.markdown(f"""
        <div class="warning-banner" style="text-align:center; font-size:1.2rem;">
            ⚠️ NEGOTIATION FAILED — Case escalated to trial
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 Retry Negotiation", key="retry"):
            del st.session_state[neg_key]
            st.rerun()
