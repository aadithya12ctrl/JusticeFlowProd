# agents/emotion_agent.py — Emotional Intelligence Layer
import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


EMOTION_PROMPT = PromptTemplate.from_template("""
Analyze the emotional state conveyed in this legal filing or message.
Return JSON only, no markdown, no explanation:
{{
  "temperature": <int 0-100>,
  "dominant_emotion": "<anger|fear|grief|frustration|neutral>",
  "recommendation": "<one sentence mediator action>"
}}
0 = completely calm, 100 = explosive emotional state.
Text: {text}
""")

EMOTION_COLORS = {"anger":"#B03A2E","fear":"#D4A843","grief":"#8B5E3C","frustration":"#C0522B","neutral":"#6B8F71"}
EMOTION_ICONS = {"anger":"🔥","fear":"😰","grief":"💔","frustration":"😤","neutral":"😌"}


def analyze_emotion(text: str, llm) -> dict:
    chain = EMOTION_PROMPT | llm | StrOutputParser()
    try:
        raw = chain.invoke({"text": text})
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"): raw = raw[:-3]
            raw = raw.strip()
        data = json.loads(raw)
        temperature = max(0, min(100, int(data.get("temperature", 50))))
        emotion = data.get("dominant_emotion", "neutral").lower()
        if emotion not in EMOTION_COLORS: emotion = "neutral"
        return {"temperature": temperature, "dominant_emotion": emotion, "recommendation": data.get("recommendation", "Continue monitoring the situation.")}
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return {"temperature": 50, "dominant_emotion": "neutral", "recommendation": "Unable to analyze emotion. Continue with standard procedures."}
