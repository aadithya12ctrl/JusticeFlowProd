# pages/page_08_live_demo.py — 🎤 Live Demo: Audience Judge Interaction
# Pre-loaded Indian RERA case. One-click start. Audience types judge directions.
# Designed as the "wow-closer" for pitch presentations.

import streamlit as st
import json, os, sys, uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.theme import page_header
from config import get_llm
from db.database import insert_case, update_case, insert_negotiation_turn
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ─── Demo Case: Indian RERA Builder vs Homebuyer ─────────────────────

DEMO_CASE = {
    "title": "Sharma v. Prestige Skyline Builders Pvt. Ltd.",
    "description": (
        "Homebuyer Rajesh Sharma booked a 3BHK apartment in Prestige Skyline Estate, Bangalore "
        "for ₹1,20,00,000 in 2022. The builder promised possession by March 2025 under RERA "
        "registration. As of February 2026, possession has not been delivered — the project is "
        "only 60% complete. The builder has not provided updated completion timelines despite "
        "multiple written requests. Mr. Sharma has been paying EMIs of ₹85,000/month on a home "
        "loan while also paying ₹35,000/month rent for alternative accommodation. He seeks "
        "₹12,00,000 in compensation for delayed possession, mental agony, and rental expenses, "
        "or alternatively, a full refund with 10% annual interest under Section 18 of RERA."
    ),
    "category": "contract",
    "jurisdiction": "Karnataka RERA Authority (K-RERA)",
    "claim_amount": 1200000,
    "plaintiff_name": "Rajesh Sharma",
    "defendant_name": "Prestige Skyline Builders Pvt. Ltd.",
    "plaintiff_interests": (
        "Seeking ₹12,00,000 compensation for delayed possession under RERA Section 18. "
        "Has documented evidence: registered agreement, payment receipts, EMI statements, "
        "rent receipts, and 14 written complaints to the builder. Willing to accept possession "
        "with adequate compensation as an alternative to refund."
    ),
    "defendant_interests": (
        "Builder claims delays due to COVID-19 force majeure and municipal approval bottlenecks. "
        "Argues RERA timeline should be extended by 18 months. Willing to offer ₹2,00,000 as "
        "goodwill gesture but disputes the ₹12,00,000 claim as excessive. Project will be "
        "completed by December 2026."
    ),
}

# ─── Agent Prompts (India-tuned for demo) ────────────────────────────

PLAINTIFF_PROMPT = PromptTemplate.from_template("""
SYSTEM: You are the Plaintiff's Legal Advocate AI in an Indian RERA dispute.
You ALWAYS argue in favor of the homebuyer. Cite RERA Act 2016, Indian Contract Act,
Consumer Protection Act 2019, and relevant NCDRC/RERA Authority precedents.
Be persuasive, professional, and cite specific sections of Indian law.
If the presiding judge has given directions, you MUST acknowledge and respond to them respectfully.

CASE: {case_summary}
PLAINTIFF INTERESTS: {plaintiff_interests}
ORIGINAL CLAIM: ₹{claim_amount}
CURRENT OFFER ON TABLE: ₹{current_offer}
ROUND: {round} of {max_rounds}

FULL NEGOTIATION HISTORY:
{history}

{human_input}

Respond with JSON only, no markdown:
{{"message": "<your 2-4 sentence argument citing SPECIFIC Indian law sections>", "proposed_amount": <float>, "willing_to_settle": <true/false>}}
""")

DEFENDANT_PROMPT = PromptTemplate.from_template("""
SYSTEM: You are the Defendant Builder's Legal Advocate AI in an Indian RERA dispute.
You argue in favor of the builder/developer. Cite force majeure clauses, RERA extension provisions,
and relevant builder-favorable precedents from Indian courts.
Be strategic but fair. Minimize liability while appearing reasonable.
If the presiding judge has given directions, you MUST acknowledge and respond to them respectfully.

CASE: {case_summary}
DEFENDANT INTERESTS: {defendant_interests}
ORIGINAL CLAIM: ₹{claim_amount}
CURRENT OFFER ON TABLE: ₹{current_offer}
ROUND: {round} of {max_rounds}

FULL NEGOTIATION HISTORY:
{history}

{human_input}

Respond with JSON only, no markdown:
{{"message": "<your 2-4 sentence counter-argument citing Indian legal defenses>", "proposed_amount": <float>, "willing_to_settle": <true/false>}}
""")

# ─── Helpers ─────────────────────────────────────────────────────────

def _clean_json(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"): raw = raw[:-3]
    return raw.strip()


def _format_history(history: list[dict]) -> str:
    if not history:
        return "(No exchanges yet — opening round.)"
    lines = []
    for h in history:
        role = h.get("role", "")
        icon = "🟠" if "Plaintiff" in role else "🟤" if "Defendant" in role else "👨‍⚖️"
        lines.append(f"[{icon} {role}]: {h['message']} (₹{h.get('amount', 'N/A'):,.0f})")
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
        return {
            "message": "I maintain my current position and await the court's direction.",
            "amount": params.get("current_offer", 0),
            "willing": False,
        }


# ─── Main Render ─────────────────────────────────────────────────────

def render():
    # Dramatic header
    st.markdown("""
    <div style="text-align:center; padding:1.5rem 0 0.5rem 0;">
        <div style="display:inline-block; background:#B03A2E; color:white; padding:0.3rem 1.2rem;
                    border-radius:20px; font-size:0.85rem; font-weight:700; letter-spacing:0.15em;
                    animation: pulse 2s infinite; margin-bottom:0.8rem;">
            🔴 LIVE DEMO
        </div>
        <h1 style="font-size:2.2rem; color:#2C1A0E; margin:0.5rem 0 0.3rem 0; font-weight:800;">
            AI Negotiation — Audience Interaction
        </h1>
        <p style="color:#6B4C35; font-size:1.1rem; max-width:700px; margin:0 auto;">
            Type a judicial direction and watch two AI agents react in real-time.
        </p>
    </div>
    <style>
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.85; transform: scale(1.05); }
        }
    </style>
    """, unsafe_allow_html=True)

    # ─── Session state ───────────────────────────────────────────
    if "live_demo" not in st.session_state:
        st.session_state.live_demo = {
            "status": "ready",  # ready | running | settled | failed
            "case_id": None,
            "history": [],
            "current_offer": DEMO_CASE["claim_amount"],
            "round": 0,
            "max_rounds": 7,
        }
    demo = st.session_state.live_demo

    # ─── READY: Show case brief + start button ───────────────────
    if demo["status"] == "ready":
        st.markdown("---")

        # Case card
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#2C1A0E,#3D2818);
                    border-radius:16px; padding:2rem; margin:1rem 0; color:#F5F0E8;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <span style="font-size:1.4rem; font-weight:700;">📋 {DEMO_CASE['title']}</span>
                <span style="background:#C0522B; padding:0.3rem 1rem; border-radius:8px;
                             font-size:0.85rem; font-weight:600;">RERA DISPUTE</span>
            </div>
            <p style="color:#F5F0E8; opacity:0.9; line-height:1.7; font-size:0.95rem;">
                {DEMO_CASE['description']}
            </p>
            <div style="display:flex; gap:2rem; margin-top:1.5rem; flex-wrap:wrap;">
                <div>
                    <div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em; opacity:0.6;">Claim Amount</div>
                    <div style="font-size:1.6rem; font-weight:800; color:#D4A843;">₹12,00,000</div>
                </div>
                <div>
                    <div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em; opacity:0.6;">Jurisdiction</div>
                    <div style="font-size:1.1rem; font-weight:600;">K-RERA Authority</div>
                </div>
                <div>
                    <div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em; opacity:0.6;">Law Applicable</div>
                    <div style="font-size:1.1rem; font-weight:600;">RERA Act 2016, §18</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Parties
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div style="background:#C0522B22; border-left:4px solid #C0522B; border-radius:0 12px 12px 0;
                        padding:1rem; margin:0.5rem 0;">
                <strong style="color:#C0522B;">🟠 Plaintiff — {DEMO_CASE['plaintiff_name']}</strong>
                <p style="color:#2C1A0E; font-size:0.9rem; margin:0.5rem 0 0 0;">{DEMO_CASE['plaintiff_interests']}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div style="background:#8B5E3C22; border-left:4px solid #8B5E3C; border-radius:0 12px 12px 0;
                        padding:1rem; margin:0.5rem 0;">
                <strong style="color:#8B5E3C;">🟤 Defendant — {DEMO_CASE['defendant_name']}</strong>
                <p style="color:#2C1A0E; font-size:0.9rem; margin:0.5rem 0 0 0;">{DEMO_CASE['defendant_interests']}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("⚡ Begin Live Negotiation", use_container_width=True, type="primary"):
            # Create the demo case in the database
            case_id = insert_case(
                title=DEMO_CASE["title"],
                description=DEMO_CASE["description"],
                category=DEMO_CASE["category"],
                jurisdiction=DEMO_CASE["jurisdiction"],
                claim_amount=DEMO_CASE["claim_amount"],
                plaintiff_name=DEMO_CASE["plaintiff_name"],
                defendant_name=DEMO_CASE["defendant_name"],
            )
            demo["case_id"] = case_id
            demo["status"] = "running"
            demo["round"] = 1
            demo["history"] = []
            demo["current_offer"] = DEMO_CASE["claim_amount"]
            update_case(case_id, status="negotiating")
            st.rerun()

    # ─── RENDER NEGOTIATION TRANSCRIPT ───────────────────────────
    if demo["history"]:
        st.markdown("---")
        st.markdown("### 💬 Live Negotiation Transcript")
        for entry in demo["history"]:
            role = entry.get("role", "")
            msg = entry.get("message", "")
            amt = entry.get("amount", 0)

            if "Plaintiff" in role:
                st.markdown(f"""
                <div style="background:#C0522B15; border-left:5px solid #C0522B; border-radius:0 14px 14px 0;
                            padding:1rem 1.2rem; margin:0.6rem 0;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong style="color:#C0522B; font-size:1rem;">🟠 {role}</strong>
                        <span style="color:#C0522B; font-weight:800; font-size:1.1rem;">₹{amt:,.0f}</span>
                    </div>
                    <p style="color:#2C1A0E; margin:0.4rem 0 0 0; line-height:1.6;">{msg}</p>
                </div>
                """, unsafe_allow_html=True)
            elif "Defendant" in role:
                st.markdown(f"""
                <div style="background:#8B5E3C15; border-left:5px solid #8B5E3C; border-radius:0 14px 14px 0;
                            padding:1rem 1.2rem; margin:0.6rem 0;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong style="color:#8B5E3C; font-size:1rem;">🟤 {role}</strong>
                        <span style="color:#8B5E3C; font-weight:800; font-size:1.1rem;">₹{amt:,.0f}</span>
                    </div>
                    <p style="color:#2C1A0E; margin:0.4rem 0 0 0; line-height:1.6;">{msg}</p>
                </div>
                """, unsafe_allow_html=True)
            elif "Judge" in role:
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#D4A84333,#D4A84311);
                            border-left:5px solid #D4A843; border-radius:0 14px 14px 0;
                            padding:1rem 1.2rem; margin:0.6rem 0;">
                    <strong style="color:#D4A843; font-size:1.05rem;">👨‍⚖️ {role}</strong>
                    <p style="color:#2C1A0E; margin:0.4rem 0 0 0; font-weight:500; line-height:1.6;">{msg}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:#6B8F7122; border-left:5px solid #6B8F71; border-radius:0 14px 14px 0;
                            padding:1rem 1.2rem; margin:0.6rem 0;">
                    <strong style="color:#6B8F71;">⚖️ {role}</strong>
                    <p style="color:#2C1A0E; margin:0.4rem 0 0 0;">{msg}</p>
                </div>
                """, unsafe_allow_html=True)

    # ─── CURRENT OFFER BANNER ────────────────────────────────────
    if demo["status"] in ("running",):
        st.markdown(f"""
        <div style="text-align:center; padding:1.5rem; margin:1.5rem 0;
                    background:linear-gradient(135deg,#2C1A0E,#3D2818); border-radius:16px;
                    box-shadow: 0 4px 24px rgba(44,26,14,0.3);">
            <div style="color:#D4A843; font-size:0.8rem; text-transform:uppercase;
                        letter-spacing:0.15em; margin-bottom:0.3rem;">Current Offer on Table</div>
            <div style="color:#F5F0E8; font-size:3rem; font-weight:800;
                        text-shadow: 0 2px 8px rgba(0,0,0,0.3);">₹{demo['current_offer']:,.0f}</div>
            <div style="color:#F5F0E8; opacity:0.6; font-size:0.9rem; margin-top:0.3rem;">
                Round {demo['round']} of {demo['max_rounds']}
                &nbsp;·&nbsp; Original claim: ₹{DEMO_CASE['claim_amount']:,.0f}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ─── JUDGE INPUT PHASE ───────────────────────────────────────
    if demo["status"] == "running":
        st.markdown(f"""
        <div style="text-align:center; margin:1rem 0 0.5rem 0;">
            <h3 style="color:#2C1A0E; margin:0;">👨‍⚖️ Round {demo['round']} — The Court Speaks</h3>
            <p style="color:#6B4C35; font-size:0.95rem;">
                <em>Type your direction below. Both AI agents will acknowledge and respond to it.</em>
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Suggestion chips
        st.markdown("""
        <div style="display:flex; gap:0.5rem; flex-wrap:wrap; justify-content:center; margin-bottom:1rem;">
            <span style="background:#D4A84322; color:#6B4C35; padding:0.4rem 0.8rem;
                         border-radius:20px; font-size:0.8rem; border: 1px solid #D4A84355;">
                💡 "The court notes the builder has not provided RERA registration documents"
            </span>
            <span style="background:#D4A84322; color:#6B4C35; padding:0.4rem 0.8rem;
                         border-radius:20px; font-size:0.8rem; border: 1px solid #D4A84355;">
                💡 "Defendant must address the 11-month delay — what was the force majeure?"
            </span>
            <span style="background:#D4A84322; color:#6B4C35; padding:0.4rem 0.8rem;
                         border-radius:20px; font-size:0.8rem; border: 1px solid #D4A84355;">
                💡 "Both parties should consider the precedent of Ireo Grace Realtech"
            </span>
        </div>
        """, unsafe_allow_html=True)

        human_input = st.text_area(
            "Judge's Direction:",
            placeholder="e.g. 'The court observes that under RERA Section 18, the buyer is entitled to interest for delayed possession. Builder, present your RERA compliance certificate...'",
            height=100,
            key=f"live_judge_{demo['round']}",
            label_visibility="collapsed",
        )

        col_run, col_settle, col_end = st.columns([3, 1, 1])
        with col_run:
            run_round = st.button(
                f"▶️ Run Round {demo['round']}",
                use_container_width=True,
                type="primary",
            )
        with col_settle:
            force_settle = st.button("✅ Settle", use_container_width=True)
        with col_end:
            end_neg = st.button("🛑 Trial", use_container_width=True)

        # Force settlement
        if force_settle:
            demo["status"] = "settled"
            demo["history"].append({
                "role": "System",
                "message": f"The Honourable Court orders settlement at ₹{demo['current_offer']:,.0f}.",
                "amount": demo["current_offer"],
            })
            if demo["case_id"]:
                update_case(demo["case_id"], status="resolved",
                            settlement_text=f"Settled at ₹{demo['current_offer']:,.0f}")
            st.rerun()

        # Escalate to trial
        if end_neg:
            demo["status"] = "failed"
            demo["history"].append({
                "role": "System",
                "message": "Negotiation terminated by the Court. Case escalated to full trial.",
                "amount": demo["current_offer"],
            })
            if demo["case_id"]:
                update_case(demo["case_id"], status="escalated")
            st.rerun()

        # Run the round
        if run_round:
            # Record judge input
            if human_input and human_input.strip():
                demo["history"].append({
                    "role": "Presiding Judge",
                    "message": human_input.strip(),
                    "amount": demo["current_offer"],
                })
                human_context = f"THE PRESIDING JUDGE DIRECTS: {human_input.strip()}"
            else:
                human_context = ""

            case_summary = f"{DEMO_CASE['title']}. {DEMO_CASE['description']}"
            history_text = _format_history(demo["history"])

            llm = get_llm(temperature=0.4, max_tokens=512)

            # Plaintiff argues
            with st.spinner("🟠 Plaintiff Advocate AI is arguing..."):
                p_result = _run_agent(PLAINTIFF_PROMPT, {
                    "case_summary": case_summary,
                    "plaintiff_interests": DEMO_CASE["plaintiff_interests"],
                    "claim_amount": DEMO_CASE["claim_amount"],
                    "current_offer": demo["current_offer"],
                    "round": demo["round"],
                    "max_rounds": demo["max_rounds"],
                    "history": history_text,
                    "human_input": human_context,
                }, llm)

            demo["history"].append({
                "role": "Plaintiff Advocate AI",
                "message": p_result["message"],
                "amount": p_result["amount"],
            })
            demo["current_offer"] = p_result["amount"]

            # Defendant responds
            history_text = _format_history(demo["history"])
            with st.spinner("🟤 Defendant Advocate AI is responding..."):
                d_result = _run_agent(DEFENDANT_PROMPT, {
                    "case_summary": case_summary,
                    "defendant_interests": DEMO_CASE["defendant_interests"],
                    "claim_amount": DEMO_CASE["claim_amount"],
                    "current_offer": demo["current_offer"],
                    "round": demo["round"],
                    "max_rounds": demo["max_rounds"],
                    "history": history_text,
                    "human_input": human_context,
                }, llm)

            demo["history"].append({
                "role": "Defendant Advocate AI",
                "message": d_result["message"],
                "amount": d_result["amount"],
            })
            demo["current_offer"] = d_result["amount"]

            # Save to DB
            if demo["case_id"]:
                insert_negotiation_turn(demo["case_id"], demo["round"], "human_mediator", human_input or "(no input)")
                insert_negotiation_turn(demo["case_id"], demo["round"], "agent_plaintiff", f"{p_result['message']} [₹{p_result['amount']:,.0f}]")
                insert_negotiation_turn(demo["case_id"], demo["round"], "agent_defendant", f"{d_result['message']} [₹{d_result['amount']:,.0f}]")

            # Check settlement
            if p_result["willing"] and d_result["willing"]:
                avg = (p_result["amount"] + d_result["amount"]) / 2
                demo["current_offer"] = avg
                demo["status"] = "settled"
                demo["history"].append({
                    "role": "System",
                    "message": f"Both parties have agreed to settle at ₹{avg:,.0f}!",
                    "amount": avg,
                })
                if demo["case_id"]:
                    update_case(demo["case_id"], status="resolved",
                                settlement_text=f"Settled at ₹{avg:,.0f}")
            elif demo["round"] >= demo["max_rounds"]:
                demo["status"] = "failed"
                demo["history"].append({
                    "role": "System",
                    "message": "Maximum rounds reached. Case escalated to full trial.",
                    "amount": demo["current_offer"],
                })
                if demo["case_id"]:
                    update_case(demo["case_id"], status="escalated")
            else:
                demo["round"] += 1

            st.rerun()

    # ─── SETTLEMENT ──────────────────────────────────────────────
    if demo["status"] == "settled":
        st.markdown(f"""
        <div style="text-align:center; padding:2rem; margin:1.5rem 0;
                    background:linear-gradient(135deg,#1a5a2a,#2d7a3f);
                    border-radius:16px; box-shadow: 0 4px 24px rgba(26,90,42,0.3);">
            <div style="font-size:3rem; margin-bottom:0.5rem;">🎉</div>
            <div style="color:#F5F0E8; font-size:1.8rem; font-weight:800;">SETTLEMENT REACHED</div>
            <div style="color:#F5F0E8; font-size:2.5rem; font-weight:800; margin:0.5rem 0;">₹{demo['current_offer']:,.0f}</div>
            <div style="color:#F5F0E8; opacity:0.8; font-size:1rem;">
                Resolved in {demo['round']} round{'s' if demo['round'] != 1 else ''}
                &nbsp;·&nbsp; Original claim: ₹{DEMO_CASE['claim_amount']:,.0f}
                &nbsp;·&nbsp; Savings: {((1 - demo['current_offer']/DEMO_CASE['claim_amount'])*100):,.0f}% reduction
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.balloons()

        if st.button("🔄 Reset Demo", use_container_width=True):
            del st.session_state.live_demo
            st.rerun()

    elif demo["status"] == "failed":
        st.markdown(f"""
        <div style="text-align:center; padding:2rem; margin:1.5rem 0;
                    background:linear-gradient(135deg,#7a2d2d,#a03a3a);
                    border-radius:16px; box-shadow: 0 4px 24px rgba(122,45,45,0.3);">
            <div style="font-size:3rem; margin-bottom:0.5rem;">⚠️</div>
            <div style="color:#F5F0E8; font-size:1.5rem; font-weight:800;">NEGOTIATION FAILED</div>
            <div style="color:#F5F0E8; opacity:0.8; font-size:1rem; margin-top:0.5rem;">
                Case escalated to full trial · Last offer: ₹{demo['current_offer']:,.0f}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 Reset Demo", use_container_width=True):
            del st.session_state.live_demo
            st.rerun()
