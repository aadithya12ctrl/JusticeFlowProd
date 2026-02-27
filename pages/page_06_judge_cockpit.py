# pages/page_06_judge_cockpit.py — Judge Summary Dashboard + PDF Brief
import streamlit as st
import json, os, sys
from datetime import datetime

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

TIME_ESTIMATES = {"rera":"8-16 weeks","rent_control":"3-6 weeks","labour_industrial":"4-8 weeks","contract_civil":"3-6 weeks","motor_accident":"6-12 weeks","consumer":"4-8 weeks","family_matrimonial":"8-16 weeks","cheque_bounce":"4-8 weeks","other":"4-8 weeks"}

# ─── Status Pipeline (for timeline) ─────────────────────────────────
PIPELINE_STAGES = [
    ("intake", "📝 Filed", "Case submitted to the system"),
    ("scored", "🧬 DNA Scored", "Case DNA vector computed and twin matched"),
    ("filtered", "🔍 Filtered", "Passed auto-filter pipeline"),
    ("negotiating", "🤝 Negotiating", "AI negotiation in progress"),
    ("resolved", "✅ Settled", "Settlement reached"),
    ("escalated", "⬆️ Escalated", "Sent to full trial"),
    ("dismissed", "❌ Dismissed", "Case dismissed"),
]

STATUS_ORDER = {s[0]: i for i, s in enumerate(PIPELINE_STAGES)}


def _generate_judge_brief(case, case_id):
    """Generate a downloadable text-based judge brief."""
    p_name = get_entity_name(case.get("plaintiff_id", ""))
    d_name = get_entity_name(case.get("defendant_id", ""))
    cat = (case.get("category", "other") or "other").replace("_", " ").title()
    dls = case.get("dls_score")
    temp = case.get("emotional_temp")
    neg_log = get_negotiation_log(case_id)

    # Find case twin
    twin_info = "No DNA analysis available."
    dna_str = case.get("dna_vector")
    if dna_str:
        try:
            dna_vec = json.loads(dna_str)
            twin, sim = find_case_twin(dna_vec, get_historical_cases())
            if twin:
                twin_info = f"Case Twin: {twin['id']} ({sim*100:.0f}% match)\n  Category: {twin.get('category','N/A')}\n  Outcome: {twin.get('outcome','N/A')}\n  Jurisdiction: {twin.get('jurisdiction','N/A')} ({twin.get('year','N/A')})"
        except:
            pass

    brief = f"""
╔══════════════════════════════════════════════════════════════════╗
║              JUSTICEFLOW — AI JUDGE BRIEF                       ║
║              Confidential Case Summary Report                   ║
╚══════════════════════════════════════════════════════════════════╝

Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p IST')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. CASE OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Case ID        : #{case_id}
  Title          : {case.get('title', 'N/A')}
  Category       : {cat}
  Jurisdiction   : {case.get('jurisdiction', 'N/A')}
  Filed          : {case.get('filed_at', 'N/A')}
  Status         : {case.get('status', 'intake').upper()}
  Claim Amount   : ₹{case.get('claim_amount', 0):,.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. PARTIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Plaintiff      : {p_name}
  Defendant      : {d_name}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. AI RISK ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Dismissal Likelihood (DLS) : {f'{float(dls):.0f}/100' if dls is not None else 'Not scored'}
  Litigation Risk Score      : {f'{float(temp):.0f}/100' if temp is not None else 'Not analyzed'}
  Est. Time to Resolution    : {TIME_ESTIMATES.get(case.get('category', 'other'), '4-8 weeks')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. CASE DNA & PRECEDENT MATCHING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {twin_info}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. AI RECOMMENDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {case.get('ai_outcome', 'No AI recommendation generated yet.')}
  Confidence: {f"{float(case.get('ai_confidence', 0)):.0f}%" if case.get('ai_confidence') else 'N/A'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6. NEGOTIATION HISTORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    if neg_log:
        brief += f"\n  Total Turns: {len(neg_log)}"
        if case.get("settlement_text"):
            brief += f"\n  Settlement: {case['settlement_text']}"
        brief += "\n"
        for entry in neg_log[:10]:
            brief += f"\n  [{entry.get('speaker','?')}] Turn {entry.get('turn','?')}:"
            brief += f"\n    {entry.get('message','')[:120]}"
    else:
        brief += "\n  No negotiation conducted."

    brief += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
7. CASE DESCRIPTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {case.get('description', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  This report was auto-generated by JusticeFlow AI.
  It is advisory in nature and does not constitute a legal opinion.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    return brief


def _render_case_timeline(case):
    """Render a visual case pipeline timeline."""
    current_status = case.get("status", "intake")
    current_idx = STATUS_ORDER.get(current_status, 0)

    # Determine which stages to show (the linear pipeline + terminal state)
    linear_stages = PIPELINE_STAGES[:4]  # intake → scored → filtered → negotiating
    terminal = None
    if current_status in ("resolved", "escalated", "dismissed"):
        for s in PIPELINE_STAGES:
            if s[0] == current_status:
                terminal = s
                break

    st.markdown("### 📋 Case Pipeline")

    timeline_html = '<div style="display:flex; align-items:center; gap:0; margin:1rem 0; flex-wrap:wrap;">'

    for i, (status_key, label, desc) in enumerate(linear_stages):
        stage_idx = STATUS_ORDER[status_key]
        if stage_idx < current_idx or current_status == status_key:
            bg = "#6B8F71"
            color = "#F5F0E8"
            opacity = "1"
            border = "2px solid #6B8F71"
        elif terminal and STATUS_ORDER.get(terminal[0], 99) > stage_idx:
            bg = "#6B8F71"
            color = "#F5F0E8"
            opacity = "1"
            border = "2px solid #6B8F71"
        else:
            bg = "#EDE3D4"
            color = "#6B4C35"
            opacity = "0.5"
            border = "2px solid #D4C4B0"

        timeline_html += f'''
        <div style="text-align:center; flex:1; min-width:100px;">
            <div style="background:{bg}; color:{color}; width:36px; height:36px; border-radius:50%;
                        display:flex; align-items:center; justify-content:center; margin:0 auto;
                        font-size:0.9rem; border:{border}; opacity:{opacity};">{label.split(" ")[0]}</div>
            <div style="font-size:0.75rem; color:#2C1A0E; margin-top:0.3rem; font-weight:600; opacity:{opacity};">{label.split(" ", 1)[1] if " " in label else label}</div>
        </div>'''

        if i < len(linear_stages) - 1:
            arrow_color = "#6B8F71" if stage_idx < current_idx else "#D4C4B0"
            timeline_html += f'<div style="font-size:1.2rem; color:{arrow_color}; margin:0 -0.3rem;">→</div>'

    # Terminal state
    if terminal:
        t_key, t_label, t_desc = terminal
        if t_key == "resolved":
            t_bg, t_color = "#6B8F71", "#F5F0E8"
        elif t_key == "escalated":
            t_bg, t_color = "#D4A843", "#2C1A0E"
        else:
            t_bg, t_color = "#B03A2E", "#F5F0E8"

        timeline_html += f'<div style="font-size:1.2rem; color:#6B8F71; margin:0 -0.3rem;">→</div>'
        timeline_html += f'''
        <div style="text-align:center; flex:1; min-width:100px;">
            <div style="background:{t_bg}; color:{t_color}; width:36px; height:36px; border-radius:50%;
                        display:flex; align-items:center; justify-content:center; margin:0 auto;
                        font-size:0.9rem; border:2px solid {t_bg};">{t_label.split(" ")[0]}</div>
            <div style="font-size:0.75rem; color:#2C1A0E; margin-top:0.3rem; font-weight:600;">{t_label.split(" ", 1)[1]}</div>
        </div>'''

    timeline_html += '</div>'
    st.markdown(timeline_html, unsafe_allow_html=True)

    # Stage details strip
    details = []
    if case.get("dna_vector"): details.append("🧬 DNA")
    if case.get("dls_score") is not None: details.append("📊 DLS")
    if case.get("filter_result"): details.append("🔍 Filter")
    if case.get("emotional_temp") is not None: details.append("📈 Risk")
    neg_log = get_negotiation_log(case.get("id", ""))
    if neg_log: details.append(f"🤝 {len(neg_log)} turns")
    if case.get("ai_outcome"): details.append("📜 Citations")

    if details:
        chips = " ".join(
            f'<span style="background:#D4A84322; color:#6B4C35; padding:0.2rem 0.6rem; border-radius:12px; font-size:0.75rem; border:1px solid #D4A84355;">{d}</span>'
            for d in details
        )
        st.markdown(f'<div style="text-align:center; margin-top:0.5rem;">{chips}</div>', unsafe_allow_html=True)


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

    # ─── Case Pipeline Timeline ──────────────────────────────────
    _render_case_timeline(case)

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── AI Signal Cards ─────────────────────────────────────────
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        dls = case.get("dls_score")
        val = f"{float(dls):.0f}/100" if dls is not None else "Not scored"
        st.markdown(f'<div class="judge-card"><h4>DLS Score</h4><div class="value" style="font-size:{"1.8rem" if dls else "1rem"};{"" if dls else "opacity:0.6;"}">{val}</div></div>', unsafe_allow_html=True)
    with c2:
        temp = case.get("emotional_temp")
        if temp is not None:
            tc = "#6B8F71" if float(temp)<30 else "#D4A843" if float(temp)<60 else "#B03A2E"
            st.markdown(f'<div class="judge-card"><h4>Risk Score</h4><div class="value" style="color:{tc};">{float(temp):.0f}/100</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="judge-card"><h4>Risk Score</h4><div class="value" style="font-size:1rem;opacity:0.6;">Not analyzed</div></div>', unsafe_allow_html=True)
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

    # ─── Action Buttons Row ──────────────────────────────────────
    col_cite, col_pdf = st.columns(2)
    with col_cite:
        gen_citations = st.button("📜 Generate Citations & AI Recommendation", use_container_width=True)
    with col_pdf:
        brief_text = _generate_judge_brief(case, case_id)
        st.download_button(
            "📄 Download Judge Brief",
            brief_text,
            file_name=f"JudgeBrief_{case_id}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    if gen_citations:
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
        st.markdown(f"**Claim:** ₹{case.get('claim_amount',0):,.2f}")
        st.markdown(f"**Description:** {case['description']}")
