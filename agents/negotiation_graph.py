# agents/negotiation_graph.py — Multi-agent negotiation engine
import json
from typing import TypedDict, Annotated
import operator
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

class NegotiationState(TypedDict):
    case_id: str
    case_summary: str
    plaintiff_interests: str
    defendant_interests: str
    claim_amount: float
    turn: int
    max_turns: int
    history: Annotated[list[dict], operator.add]
    current_offer: float
    plaintiff_accepted: bool
    defendant_accepted: bool
    settlement_text: str
    status: str

PLAINTIFF_PROMPT = PromptTemplate.from_template("""
You are an AI agent representing the PLAINTIFF.
Case: {case_summary}
Interests: {plaintiff_interests}
Claim: ${claim_amount}. Current Offer: ${current_offer}. Turn {turn}/{max_turns}.
History: {history}
If offer is fair (within 15%), accept. Start strong, then compromise.
Return JSON only, no markdown:
{{"message": "<2-3 sentences citing legal principle>", "counter_offer": <float>, "accept": <true/false>}}
""")

DEFENDANT_PROMPT = PromptTemplate.from_template("""
You are an AI agent representing the DEFENDANT.
Case: {case_summary}
Interests: {defendant_interests}
Claim: ${claim_amount}. Current Offer: ${current_offer}. Turn {turn}/{max_turns}.
History: {history}
Minimize liability but be reasonable. Accept if offer is fair.
Return JSON only, no markdown:
{{"message": "<2-3 sentences citing legal principle>", "counter_offer": <float>, "accept": <true/false>}}
""")

MEDIATOR_PROMPT = PromptTemplate.from_template("""
You are a neutral AI mediator. Case: {case_summary}
Offer: ${current_offer}. Claim: ${claim_amount}. Turn {turn}/{max_turns}. Gap: ${gap}.
Suggest compromise. Return JSON only, no markdown:
{{"message": "<1-2 sentence hint>", "suggested_offer": <float>}}
""")

def _fmt(history):
    if not history: return "No prior exchanges."
    return "\n".join(f"[{h['speaker']}]: {h['message']} (${h.get('offer_amount','N/A')})" for h in history[-6:])

def _clean(raw):
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n",1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"): raw = raw[:-3]
    return raw.strip()

def plaintiff_node(state, llm):
    chain = PLAINTIFF_PROMPT | llm | StrOutputParser()
    try:
        raw = chain.invoke({"case_summary":state["case_summary"],"plaintiff_interests":state["plaintiff_interests"],"claim_amount":state["claim_amount"],"current_offer":state["current_offer"],"turn":state["turn"],"max_turns":state["max_turns"],"history":_fmt(state["history"])})
        data = json.loads(_clean(raw))
        offer = float(data.get("counter_offer", state["current_offer"]))
        return {"history":[{"speaker":"Plaintiff Agent","message":data.get("message",""),"offer_amount":offer}],"current_offer":offer,"plaintiff_accepted":bool(data.get("accept",False))}
    except: return {"history":[{"speaker":"Plaintiff Agent","message":"I maintain my position.","offer_amount":state["current_offer"]}],"plaintiff_accepted":False}

def defendant_node(state, llm):
    chain = DEFENDANT_PROMPT | llm | StrOutputParser()
    try:
        raw = chain.invoke({"case_summary":state["case_summary"],"defendant_interests":state["defendant_interests"],"claim_amount":state["claim_amount"],"current_offer":state["current_offer"],"turn":state["turn"],"max_turns":state["max_turns"],"history":_fmt(state["history"])})
        data = json.loads(_clean(raw))
        offer = float(data.get("counter_offer", state["current_offer"]))
        return {"history":[{"speaker":"Defendant Agent","message":data.get("message",""),"offer_amount":offer}],"current_offer":offer,"defendant_accepted":bool(data.get("accept",False))}
    except: return {"history":[{"speaker":"Defendant Agent","message":"We need more time.","offer_amount":state["current_offer"]}],"defendant_accepted":False}

def mediator_node(state, llm):
    if state.get("plaintiff_accepted") and state.get("defendant_accepted"):
        return {"status":"settled","settlement_text":f"Settlement at ${state['current_offer']:,.2f}","history":[{"speaker":"Mediator","message":f"Both parties accepted ${state['current_offer']:,.2f}. Settlement reached!","offer_amount":state["current_offer"]}]}
    if state["turn"] >= state["max_turns"]:
        return {"status":"failed","history":[{"speaker":"Mediator","message":"Max rounds reached. Case escalated to trial.","offer_amount":state["current_offer"]}]}
    po = do = state["current_offer"]
    for h in reversed(state.get("history",[])):
        if h["speaker"]=="Plaintiff Agent": po=h.get("offer_amount",po); break
    for h in reversed(state.get("history",[])):
        if h["speaker"]=="Defendant Agent": do=h.get("offer_amount",do); break
    gap = abs(po-do)
    if state["turn"] >= 8:
        s = (po+do)/2
        return {"history":[{"speaker":"Mediator","message":f"Final rounds. Accept ${s:,.2f} to avoid trial.","offer_amount":s}],"current_offer":s,"turn":state["turn"]+1}
    chain = MEDIATOR_PROMPT | llm | StrOutputParser()
    try:
        raw = chain.invoke({"case_summary":state["case_summary"],"current_offer":state["current_offer"],"claim_amount":state["claim_amount"],"turn":state["turn"],"max_turns":state["max_turns"],"gap":gap})
        data = json.loads(_clean(raw))
        s = float(data.get("suggested_offer",state["current_offer"]))
        return {"history":[{"speaker":"Mediator","message":data.get("message",""),"offer_amount":s}],"current_offer":s,"turn":state["turn"]+1}
    except: return {"history":[{"speaker":"Mediator","message":"Let's continue.","offer_amount":state["current_offer"]}],"turn":state["turn"]+1}

def run_negotiation(case_id, case_summary, plaintiff_interests, defendant_interests, claim_amount, llm, max_turns=10):
    state = {"case_id":case_id,"case_summary":case_summary,"plaintiff_interests":plaintiff_interests,"defendant_interests":defendant_interests,"claim_amount":claim_amount,"turn":1,"max_turns":max_turns,"history":[],"current_offer":claim_amount,"plaintiff_accepted":False,"defendant_accepted":False,"settlement_text":"","status":"negotiating"}
    for turn in range(1, max_turns+1):
        state["turn"] = turn
        pu = plaintiff_node(state, llm); state["history"]+=pu.get("history",[]); state["current_offer"]=pu.get("current_offer",state["current_offer"]); state["plaintiff_accepted"]=pu.get("plaintiff_accepted",False)
        du = defendant_node(state, llm); state["history"]+=du.get("history",[]); state["current_offer"]=du.get("current_offer",state["current_offer"]); state["defendant_accepted"]=du.get("defendant_accepted",False)
        mu = mediator_node(state, llm); state["history"]+=mu.get("history",[]); state["current_offer"]=mu.get("current_offer",state["current_offer"]); state["turn"]=mu.get("turn",state["turn"])
        if mu.get("status"): state["status"]=mu["status"]
        if mu.get("settlement_text"): state["settlement_text"]=mu["settlement_text"]
        if state["status"] in ("settled","failed"): break
    if state["status"]=="negotiating": state["status"]="failed"
    return state
