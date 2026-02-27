# utils/i18n.py — Hindi / English label translations
# Usage: from utils.i18n import t, get_lang
# t("key") returns Hindi or English based on session state

import streamlit as st

TRANSLATIONS = {
    # ─── Sidebar ─────────────────────────────
    "app_title": {"en": "⚖️ JusticeFlow", "hi": "⚖️ न्यायप्रवाह"},
    "app_subtitle": {"en": "AI-Powered Dispute Resolution", "hi": "AI-संचालित विवाद समाधान मंच"},
    "seed_btn": {"en": "🌱 Seed Demo Data", "hi": "🌱 डेमो डेटा लोड करें"},
    "cases_in_db": {"en": "cases in database", "hi": "केस डेटाबेस में"},

    # ─── Home Page ───────────────────────────
    "home_title": {"en": "JusticeFlow", "hi": "न्यायप्रवाह"},
    "home_subtitle": {"en": "AI-Powered Dispute Resolution Platform", "hi": "AI-संचालित विवाद समाधान मंच"},
    "crisis_source": {
        "en": "🇮🇳 Indian Judicial Crisis — Source: National Judicial Data Grid (NJDG), 2024",
        "hi": "🇮🇳 भारतीय न्यायिक संकट — स्रोत: राष्ट्रीय न्यायिक डेटा ग्रिड (NJDG), 2024",
    },
    "cases_pending": {"en": "Cases Pending", "hi": "लंबित केस"},
    "avg_disposal": {"en": "Avg Disposal Time", "hi": "औसत निपटान समय"},
    "settleable": {"en": "Settleable Pre-Trial", "hi": "पूर्व-सुनवाई में निपटान योग्य"},
    "judges_per_million": {"en": "Judges per Million", "hi": "प्रति दस लाख जनसंख्या पर न्यायाधीश"},
    "home_desc": {
        "en": "JusticeFlow uses AI to transform India's overburdened courts — screening trivial cases, finding precedents in seconds, and settling disputes before they reach trial. Built for judges, lawyers, and litigants who deserve faster justice.",
        "hi": "न्यायप्रवाह AI का उपयोग करके भारत की अत्यधिक भारग्रस्त अदालतों को बदलता है — तुच्छ मामलों की छंटनी करता है, सेकंडों में पूर्व निर्णय खोजता है, और विवादों को सुनवाई से पहले निपटाता है। न्यायाधीशों, वकीलों और वादियों के लिए बनाया गया जो तेज़ न्याय के हकदार हैं।",
    },
    # Feature cards
    "feat_dna": {"en": "🧬 Case DNA", "hi": "🧬 केस DNA"},
    "feat_dna_desc": {
        "en": "AI fingerprinting matches cases to historical twins using 6D vector similarity.",
        "hi": "AI फिंगरप्रिंटिंग 6D वेक्टर समानता का उपयोग करके मामलों को ऐतिहासिक जुड़वां से मिलाता है।",
    },
    "feat_neg": {"en": "🤝 Negotiation AI", "hi": "🤝 बातचीत AI"},
    "feat_neg_desc": {
        "en": "Multi-agent system mediates autonomously between plaintiff and defendant.",
        "hi": "मल्टी-एजेंट सिस्टम वादी और प्रतिवादी के बीच स्वायत्त रूप से मध्यस्थता करता है।",
    },
    "feat_dls": {"en": "📊 DLS Engine", "hi": "📊 DLS इंजन"},
    "feat_dls_desc": {
        "en": "Predicts dismissal probability with per-reason breakdown and smart warnings.",
        "hi": "कारण-वार विश्लेषण और स्मार्ट चेतावनियों के साथ खारिज होने की संभावना की भविष्यवाणी करता है।",
    },
    "feat_risk": {"en": "📊 Risk Indicator", "hi": "📊 जोखिम संकेतक"},
    "feat_risk_desc": {
        "en": "Linguistic risk analysis with calibrated scoring and cooling-off alerts.",
        "hi": "अंशांकित स्कोरिंग और शीतलन चेतावनियों के साथ भाषाई जोखिम विश्लेषण।",
    },
    "feat_filter": {"en": "🔍 Auto Filter", "hi": "🔍 ऑटो फ़िल्टर"},
    "feat_filter_desc": {
        "en": "Rule-based + LLM hybrid filter catches jurisdiction issues and trivial claims.",
        "hi": "नियम-आधारित + LLM हाइब्रिड फ़िल्टर क्षेत्राधिकार मुद्दों और तुच्छ दावों को पकड़ता है।",
    },
    "feat_graph": {"en": "🕸️ Conflict Graph", "hi": "🕸️ विवाद ग्राफ़"},
    "feat_graph_desc": {
        "en": "NetworkX-powered graph reveals repeat offenders and systemic abuse patterns.",
        "hi": "NetworkX-संचालित ग्राफ़ बार-बार अपराधियों और व्यवस्थित दुरुपयोग पैटर्न को उजागर करता है।",
    },
    "active_cases": {"en": "Active Cases", "hi": "सक्रिय केस"},
    "entities": {"en": "Entities", "hi": "संस्थाएं"},
    "historical_cases": {"en": "Historical Cases", "hi": "ऐतिहासिक केस"},
    "ai_model": {"en": "AI Model", "hi": "AI मॉडल"},

    # ─── File Case Page ──────────────────────
    "file_title": {"en": "File a Case", "hi": "केस दर्ज करें"},
    "file_subtitle": {"en": "Submit a new dispute for AI-powered analysis", "hi": "AI-संचालित विश्लेषण के लिए नया विवाद दर्ज करें"},
    "case_title": {"en": "📋 Case Title", "hi": "📋 केस शीर्षक"},
    "case_title_placeholder": {"en": "e.g. Landlord Heating Dispute", "hi": "जैसे: मकान मालिक विवाद"},
    "plaintiff_name": {"en": "👤 Plaintiff Name", "hi": "👤 वादी का नाम"},
    "plaintiff_placeholder": {"en": "e.g. John Smith", "hi": "जैसे: रमेश कुमार"},
    "category": {"en": "📂 Category", "hi": "📂 श्रेणी"},
    "claim_amount": {"en": "💰 Claim Amount (₹)", "hi": "💰 दावा राशि (₹)"},
    "defendant_name": {"en": "👤 Defendant Name", "hi": "👤 प्रतिवादी का नाम"},
    "defendant_placeholder": {"en": "e.g. Greenfield Properties LLC", "hi": "जैसे: ग्रीनफील्ड प्रॉपर्टीज प्रा. लि."},
    "jurisdiction": {"en": "🏛️ Jurisdiction", "hi": "🏛️ क्षेत्राधिकार"},
    "jurisdiction_placeholder": {"en": "e.g. Municipal Court", "hi": "जैसे: जिला न्यायालय, बैंगलोर"},
    "description": {"en": "📝 Case Description", "hi": "📝 केस विवरण"},
    "description_placeholder": {
        "en": "Describe the dispute in detail. Include relevant dates, events, and damages...",
        "hi": "विवाद का विस्तार से वर्णन करें। प्रासंगिक तिथियां, घटनाएं और क्षति शामिल करें...",
    },
    "submit_btn": {"en": "⚖️ Submit Case & Generate DNA", "hi": "⚖️ केस दर्ज करें और DNA उत्पन्न करें"},
    "fill_required": {
        "en": "⚠️ Please fill in all required fields: Title, Description, Plaintiff, and Defendant.",
        "hi": "⚠️ कृपया सभी आवश्यक फ़ील्ड भरें: शीर्षक, विवरण, वादी और प्रतिवादी।",
    },
    "filing_spinner": {"en": "🧬 Filing case and computing DNA vector...", "hi": "🧬 केस दर्ज हो रहा है और DNA वेक्टर की गणना हो रही है..."},
    "case_dna_vector": {"en": "🧬 Case DNA Vector", "hi": "🧬 केस DNA वेक्टर"},
    "case_twin_found": {"en": "🔗 Case Twin Found", "hi": "🔗 समान केस मिला"},
    "dna_comparison": {"en": "🧬 Case DNA Comparison", "hi": "🧬 केस DNA तुलना"},
}


def get_lang() -> str:
    """Return 'hi' if Hindi mode is on, else 'en'."""
    return "hi" if st.session_state.get("lang_hindi", False) else "en"


def t(key: str) -> str:
    """Translate a key to the current language. Falls back to English."""
    lang = get_lang()
    entry = TRANSLATIONS.get(key, {})
    return entry.get(lang, entry.get("en", key))
