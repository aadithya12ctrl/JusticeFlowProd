# pages/page_06_judge_cockpit.py — Judge Summary Dashboard
import streamlit as st
import json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.theme import page_header
from config import get_llm
from db.database import get_all_cases, get_case, update_case, get_negotiation_log, get_entity_name, get_historical_cases
from agents.dna_agent import find_case_twin
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

STATUTE_PROMPT = PromptTemplate.from_template("""
You are an Indian legal research assistant. Given this case, cite 2-4 relevant INDIAN statutes, acts, or sections that a judge should review.
Use ONLY real Indian legislation such as:
- Indian Penal Code (IPC) sections
- Code of Civil Procedure (CPC) sections
- Code of Criminal Procedure (CrPC) sections
- Consumer Protection Act, 2019
- Transfer of Property Act, 1882
- Indian Contract Act, 1872
- Rent Control Acts (state-specific)
- Real Estate (Regulation and Development) Act (RERA), 2016
- Industrial Disputes Act, 1947
- Payment of Wages Act, 1936
- Specific Relief Act, 1963
- Limitation Act, 1963
- Negotiable Instruments Act, 1881

Return JSON only, no markdown:
{{"citations": [{{"statute": "<Act name, Section number>", "title": "<short title of the provision>", "relevance": "<one line explaining why this applies to the case>"}}], "recommended_outcome": "<brief recommendation for the judge based on Indian legal precedent>", "confidence": <int 0-100>}}
Category: {category} Summary: {summary} Jurisdiction: {jurisdiction}
""")

TIME_ESTIMATES = {"landlord_tenant":"3-6 weeks","employment":"4-8 weeks","contract":"3-6 weeks","personal_injury":"6-12 weeks","family":"8-16 weeks","small_claims":"1-3 weeks","other":"4-8 weeks"}

def render():
    page_header("Judge Cockpit", "Full case review in under 90 seconds")
    cases = get_all_cases()
    if not cases:
        st.info("📭 No cases found. File a case first.")
        return

    case_options = {f"#{c['id']} — {c['title']} [{c.get('status','?')}]": c['id'] for c in cases}
    selected = st.selectbox("Select a case", list(case_options.keys()))
    case_id = case_options[selected]
    case = get_case(case_id)
    if not case: return

    cat = (case.get("category","other") or "other").replace("_"," ").title()
    st.markdown(f'<div style="background:linear-gradient(135deg,#2C1A0E,#3D2818);color:#F5F0E8;padding:1rem 1.5rem;border-radius:12px;margin-bottom:1rem;"><span style="font-size:1.3rem;font-weight:700;">CASE #{case_id}</span> · {cat} · Filed {case.get("filed_at","N/A")} <span style="float:right;background:#C0522B;padding:0.3rem 0.8rem;border-radius:6px;font-size:0.85rem;font-weight:600;">{case.get("status","intake").upper()}</span></div>', unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        dls = case.get("dls_score")
        val = f"{float(dls):.0f}/100" if dls is not None else "Not scored"
        st.markdown(f'<div class="judge-card"><h4>DLS Score</h4><div class="value" style="font-size:{"1.8rem" if dls else "1rem"};{"" if dls else "opacity:0.6;"}">{val}</div></div>', unsafe_allow_html=True)
    with c2:
        temp = case.get("emotional_temp")
        if temp is not None:
            tc = "#6B8F71" if float(temp)<30 else "#D4A843" if float(temp)<60 else "#B03A2E"
            st.markdown(f'<div class="judge-card"><h4>Emotional Temp</h4><div class="value" style="color:{tc};">{float(temp):.0f}/100</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="judge-card"><h4>Emotional Temp</h4><div class="value" style="font-size:1rem;opacity:0.6;">Not analyzed</div></div>', unsafe_allow_html=True)
    with c3:
        dna_str = case.get("dna_vector")
        twin_text = "No DNA"
        if dna_str:
            try:
                dna_vec = json.loads(dna_str)
                twin, sim = find_case_twin(dna_vec, get_historical_cases())
                if twin:
                    twin_text = f'{twin["id"]} ({sim*100:.0f}%)<br><span style="font-size:0.75rem;opacity:0.8;">{twin["outcome"][:40]}...</span>'
            except: pass
        st.markdown(f'<div class="judge-card"><h4>Case DNA Twin</h4><div style="font-size:1rem;color:#D4A843;font-weight:600;">{twin_text}</div></div>', unsafe_allow_html=True)
    with c4:
        ao = case.get("ai_outcome")
        if ao:
            st.markdown(f'<div class="judge-card"><h4>AI Recommendation</h4><div style="font-size:0.95rem;font-weight:600;">{ao}</div><div style="font-size:0.8rem;opacity:0.7;">Confidence: {float(case.get("ai_confidence",0)):.0f}%</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="judge-card"><h4>AI Recommendation</h4><div class="value" style="font-size:1rem;opacity:0.6;">Pending</div></div>', unsafe_allow_html=True)

    neg_log = get_negotiation_log(case_id)
    if neg_log:
        st.markdown(f'<div class="judge-card" style="margin-top:0.5rem;"><h4>Negotiation Summary</h4><div style="color:#F5F0E8;">{len(neg_log)} turns · Status: {case.get("status","unknown").title()}{" · " + case.get("settlement_text","") if case.get("settlement_text") else ""}</div></div>', unsafe_allow_html=True)

    if st.button("📜 Generate Citations & AI Recommendation", use_container_width=True):
        with st.spinner("Generating..."):
            try:
                llm = get_llm()
                chain = STATUTE_PROMPT | llm | StrOutputParser()
                raw = chain.invoke({"category":case.get("category","other"), "summary":f"{case['title']}. {case['description']}", "jurisdiction":case.get("jurisdiction","Unknown")})
                raw = raw.strip()
                if raw.startswith("```"): raw = raw.split("\n",1)[1].rsplit("```",1)[0].strip()
                data = json.loads(raw)
                update_case(case_id, ai_outcome=data.get("recommended_outcome",""), ai_confidence=data.get("confidence",0))
                for cite in data.get("citations",[]):
                    st.markdown(f'<div class="metric-card"><strong style="color:#C0522B;">{cite["statute"]}</strong> — {cite["title"]}<br><span style="color:#6B4C35;">{cite["relevance"]}</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-card" style="border-left-color:#6B8F71;"><h3>AI Recommendation</h3><p>{data.get("recommended_outcome","")}</p><p style="color:#6B4C35;">Confidence: {data.get("confidence",0)}%</p></div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Failed: {str(e)[:100]}")

    st.markdown("---")
    ct, cb1, cb2 = st.columns([2,1,1])
    with ct:
        st.markdown(f'<div class="metric-card"><h3>Est. Time to Resolution</h3><div class="value">{TIME_ESTIMATES.get(case.get("category","other"),"4-8 weeks")}</div></div>', unsafe_allow_html=True)
    with cb1:
        if st.button("⬆️ ESCALATE", use_container_width=True):
            update_case(case_id, status="escalated"); st.success("Escalated."); st.rerun()
    with cb2:
        if st.button("❌ DISMISS", use_container_width=True):
            update_case(case_id, status="dismissed"); st.warning("Dismissed."); st.rerun()

    with st.expander("📋 Full Case Details"):
        st.markdown(f"**Plaintiff:** {get_entity_name(case.get('plaintiff_id',''))}")
        st.markdown(f"**Defendant:** {get_entity_name(case.get('defendant_id',''))}")
        st.markdown(f"**Claim:** ${case.get('claim_amount',0):,.2f}")
        st.markdown(f"**Description:** {case['description']}")
