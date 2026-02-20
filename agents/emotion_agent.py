# agents/emotion_agent.py — Emotional Intelligence Layer
import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


EMOTION_PROMPT = PromptTemplate.from_template("""
You are a forensic linguist calibrating emotional intensity in legal filings.
Analyze the text below and score it using this STRICT rubric:

SCORING BRACKETS (you MUST follow these — do NOT default to 70-80):
  0-15: Purely factual, no emotional language. Example: "Tenant requests deposit return per lease terms."
  16-35: Mild frustration or concern, polite tone. Example: "I am disappointed the repairs were not completed."
  36-55: Noticeable emotion, some strong words. Example: "This is unacceptable and has caused significant stress."
  56-75: Strong emotion, personal grievance. Example: "I have been treated unfairly and demand justice."
  76-90: Highly emotional, aggressive language. Example: "This is outrageous negligence that has destroyed my life!"
  91-100: Explosive, threatening, or abusive. Example: "I am FURIOUS, these criminals must PAY for what they did!"

Count the number of emotional markers: exclamation marks, ALL CAPS words, insults, threats, hyperbole, personal attacks.
- 0 markers → score 0-20
- 1-2 markers → score 20-45
- 3-5 markers → score 45-70
- 6+ markers → score 70-100

Return JSON only, no markdown:
{{"temperature": <int 0-100>, "dominant_emotion": "<anger|fear|grief|frustration|neutral>", "recommendation": "<one sentence mediator action>"}}

Text to analyze: {text}
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
