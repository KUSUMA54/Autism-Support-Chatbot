from flask import Flask, render_template, request, jsonify
from googletrans import Translator
import asyncio
import re

app = Flask(__name__)

localized_responses = {
    "symptoms": {
        "hi": "ऑटिज्म के आम लक्षण: नाम पुकारने पर प्रतिक्रिया कम, आंखों का संपर्क कम, बोलने में देरी, एक ही हरकत बार-बार करना, और आवाज/रोशनी/स्पर्श के प्रति अधिक संवेदनशीलता। ये संकेत अक्सर 12-18 महीने में दिख सकते हैं।",
        "ta": "ஆட்டிசத்தின் பொதுவான அறிகுறிகள்: பெயர் சொல்லும்போது குறைந்த பதில், கண் தொடர்பு குறைவு, பேச்சு தாமதம், ஒரே செயலை மீண்டும் செய்வது, ஒலி/ஒளி/தொடுதலுக்கு அதிக உணர்திறன். இவை 12-18 மாதங்களில் தோன்றலாம்.",
        "te": "ఆటిజం సాధారణ లక్షణాలు: పేరు పిలిచినప్పుడు స్పందన తగ్గడం, కంటి కలయిక తక్కువగా ఉండటం, మాట ఆలస్యం, అదే చర్యలను మళ్లీ మళ్లీ చేయడం, శబ్దం/వెలుగు/స్పర్శకు అధిక సున్నితత్వం. ఇవి 12-18 నెలల్లో కనిపించవచ్చు.",
        "ml": "ഓട്ടിസത്തിന്റെ സാധാരണ ലക്ഷണങ്ങൾ: പേര് വിളിക്കുമ്പോൾ പ്രതികരണം കുറവ്, കണ്ണിൽ കണ്ണോട്ട് കുറവ്, സംസാരത്തിൽ വൈകൽ്യം, ഒരേ പ്രവൃത്തി ആവർത്തിക്കൽ, ശബ്ദം/വെളിച്ചം/സ്പർശം എന്നിവയ്ക്ക് കൂടുതൽ സംവേദനശേഷി. ഇത് 12-18 മാസത്തിൽ കാണാം.",
        "kn": "ಆಟಿಸಂ ಸಾಮಾನ್ಯ ಲಕ್ಷಣಗಳು: ಹೆಸರು ಕರೆದಾಗ ಕಡಿಮೆ ಪ್ರತಿಕ್ರಿಯೆ, ಕಣ್ಣಿನ ಸಂಪರ್ಕ ಕಡಿಮೆ, ಮಾತಿನ ತಡ, ಒಂದೇ ನಡೆ ಮರುಮರು ಮಾಡುವುದು, ಶಬ್ದ/ಬೆಳಕು/ಸ್ಪರ್ಶಕ್ಕೆ ಹೆಚ್ಚು ಸಂವೇದನೆ. ಈ ಲಕ್ಷಣಗಳು 12-18 ತಿಂಗಳಲ್ಲಿ ಕಾಣಿಸಬಹುದು.",
        "bn": "অটিজমের সাধারণ লক্ষণ: নাম ধরে ডাকলে কম সাড়া, চোখে চোখে কম যোগাযোগ, কথা বলতে দেরি, একই আচরণ বারবার করা, শব্দ/আলো/স্পর্শে বেশি সংবেদনশীলতা। এই লক্ষণ ১২-১৮ মাসে দেখা যেতে পারে।"
    },
    "diagnosis": {
        "hi": "ऑटिज्म की जांच में विकासात्मक स्क्रीनिंग (18 और 24 महीने), फिर विशेषज्ञ द्वारा विस्तृत मूल्यांकन होता है। इसमें व्यवहार निरीक्षण, माता-पिता से जानकारी और मानकीकृत परीक्षण शामिल होते हैं। जल्दी निदान से बेहतर सुधार संभव है।",
        "ta": "ஆட்டிசம் கண்டறிதலில் 18 மற்றும் 24 மாதங்களில் வளர்ச்சி பரிசோதனை, பின்னர் நிபுணர் மதிப்பீடு செய்யப்படும். நடத்தை கவனிப்பு, பெற்றோர் தகவல், தரநிலைச் சோதனைகள் இதில் அடங்கும். ஆரம்ப கண்டறிதல் நல்ல முன்னேற்றத்திற்கு உதவும்.",
        "te": "ఆటిజం నిర్ధారణలో 18, 24 నెలల అభివృద్ధి స్క్రీనింగ్ తరువాత నిపుణుల సమగ్ర మూల్యాంకనం చేస్తారు. ప్రవర్తన పరిశీలన, తల్లిదండ్రుల వివరాలు, ప్రామాణిక పరీక్షలు ఉంటాయి. త్వరగా గుర్తిస్తే మంచి ఫలితాలు వస్తాయి.",
        "ml": "ഓട്ടിസം നിർണയത്തിൽ 18, 24 മാസങ്ങളിൽ വികസന സ്ക്രീനിംഗ് നടത്തി, തുടർന്ന് വിദഗ്ധരുടെ സമഗ്ര പരിശോധന നടത്തുന്നു. പെരുമാറ്റ നിരീക്ഷണം, മാതാപിതൃ വിവരങ്ങൾ, സ്റ്റാൻഡേർഡ് ടെസ്റ്റുകൾ ഉൾപ്പെടും. നേരത്തെ നിർണയം നല്ലതാണ്.",
        "kn": "ಆಟಿಸಂ ನಿರ್ಣಯದಲ್ಲಿ 18 ಮತ್ತು 24 ತಿಂಗಳಲ್ಲಿ ಅಭಿವೃದ್ಧಿ ತಪಾಸಣೆ ಮಾಡಿ, ನಂತರ ತಜ್ಞರಿಂದ ಸಮಗ್ರ ಮೌಲ್ಯಮಾಪನ ಮಾಡಲಾಗುತ್ತದೆ. ವರ್ತನೆ ಅವಲೋಕನ, ಪೋಷಕರ ಮಾಹಿತಿ, ಮಾನದಂಡ ಪರೀಕ್ಷೆಗಳು ಒಳಗೊಂಡಿರುತ್ತವೆ. ಬೇಗ ಪತ್ತೆಹಚ್ಚುವುದು ಉತ್ತಮ.",
        "bn": "অটিজম নির্ণয়ে ১৮ ও ২৪ মাসে ডেভেলপমেন্টাল স্ক্রিনিং করা হয়, তারপর বিশেষজ্ঞের বিস্তারিত মূল্যায়ন হয়। আচরণ পর্যবেক্ষণ, অভিভাবকের তথ্য এবং মানক পরীক্ষা থাকে। দ্রুত নির্ণয় হলে উন্নতি ভালো হয়।"
    },
    "treatment": {
        "hi": "ऑटिज्म में पूर्ण इलाज नहीं, लेकिन सही थेरेपी से बहुत सुधार होता है: स्पीच थेरेपी, ऑक्युपेशनल थेरेपी, बिहेवियर थेरेपी (ABA), सोशल स्किल ट्रेनिंग। जल्दी शुरू की गई इंटरवेंशन सबसे अधिक प्रभावी रहती है।",
        "ta": "ஆட்டிசத்துக்கு முழு குணம் இல்லை, ஆனால் சரியான சிகிச்சை மற்றும் தெரபியால் நல்ல முன்னேற்றம் கிடைக்கும்: பேச்சு தெரபி, ஆக்குபேஷனல் தெரபி, ABA போன்ற நடத்தை தெரபி, சமூக திறன் பயிற்சி. ஆரம்ப தலையீடு முக்கியம்.",
        "te": "ఆటిజానికి పూర్తిగా నయం చేసే చికిత్స లేదు, కానీ సరైన థెరపీలతో మంచి పురోగతి సాధ్యమే: స్పీచ్ థెరపీ, ఆక్వుపేషనల్ థెరపీ, ABA వంటి బిహేవియర్ థెరపీ, సోషల్ స్కిల్స్ ట్రైనింగ్. తొందరగా ప్రారంభిస్తే మంచిది.",
        "ml": "ഓട്ടിസത്തിന് പൂർണ്ണ ചികിത്സയില്ലെങ്കിലും ശരിയായ തെറാപ്പികളിലൂടെ നല്ല പുരോഗതി സാധ്യമാണ്: സ്പീച്ച് തെറാപ്പി, ഒക്ക്യൂപേഷണൽ തെറാപ്പി, ABA പോലുള്ള പെരുമാറ്റ തെറാപ്പി, സാമൂഹിക കഴിവ് പരിശീലനം. നേരത്തെ തുടങ്ങുന്നത് ഏറ്റവും നല്ലത്.",
        "kn": "ಆಟಿಸಂಗೆ ಸಂಪೂರ್ಣ ಗುಣಮುಖ ಚಿಕಿತ್ಸೆ ಇಲ್ಲ. ಆದರೆ ಸರಿಯಾದ ಥೆರಪಿಯಿಂದ ಉತ್ತಮ ಪ್ರಗತಿ ಸಾಧ್ಯ: ಸ್ಪೀಚ್ ಥೆರಪಿ, ಆಕ್ಯುಪೇಶನಲ್ ಥೆರಪಿ, ABA ವರ್ತನೆ ಥೆರಪಿ, ಸಾಮಾಜಿಕ ಕೌಶಲ್ಯ ತರಬೇತಿ. ಬೇಗ ಆರಂಭಿಸಿದರೆ ಹೆಚ್ಚು ಲಾಭ.",
        "bn": "অটিজমের সম্পূর্ণ নিরাময় নেই, তবে সঠিক থেরাপিতে অনেক উন্নতি হয়: স্পিচ থেরাপি, অকুপেশনাল থেরাপি, ABA ধরনের বিহেভিয়ার থেরাপি, সামাজিক দক্ষতা প্রশিক্ষণ। যত তাড়াতাড়ি শুরু করা যায় তত ভালো।"
    },
    "communication": {
        "hi": "संचार सुधारने के लिए सरल भाषा का उपयोग करें, बच्चे को जवाब देने के लिए समय दें, चित्र/इशारों का सहारा लें, और हर छोटे प्रयास की प्रशंसा करें। नियमित अभ्यास और धैर्य से संचार कौशल बेहतर होते हैं।",
        "ta": "தொடர்பு மேம்படுத்த எளிய சொற்களைப் பயன்படுத்துங்கள், குழந்தைக்கு பதில் சொல்ல நேரம் கொடுங்கள், படம்/சைகை உதவிகளைப் பயன்படுத்துங்கள், சிறிய முயற்சியையும் பாராட்டுங்கள். தொடர்ந்து பயிற்சி செய்தால் முன்னேற்றம் காணலாம்.",
        "te": "కమ్యూనికేషన్ మెరుగుపరచడానికి సులభమైన మాటలు ఉపయోగించండి, బిడ్డకు సమాధానం చెప్పడానికి సమయం ఇవ్వండి, చిత్రాలు/సైగలు ఉపయోగించండి, చిన్న ప్రయత్నాన్నీ ప్రశంసించండి. నిరంతర అభ్యాసంతో కమ్యూనికేషన్ మెరుగవుతుంది.",
        "ml": "ആശയവിനിമയം മെച്ചപ്പെടുത്താൻ ലളിതമായ ഭാഷ ഉപയോഗിക്കുക, കുട്ടിക്ക് മറുപടി പറയാൻ സമയം കൊടുക്കുക, ചിത്രം/സിഗ്നൽ സഹായങ്ങൾ ഉപയോഗിക്കുക, ചെറു ശ്രമങ്ങളും പ്രശംസിക്കുക. സ്ഥിരമായ പരിശീലനം ഫലം നൽകും.",
        "kn": "ಸಂವಹನ ಸುಧಾರಿಸಲು ಸರಳ ಭಾಷೆ ಬಳಸಿ, ಮಗುವಿಗೆ ಪ್ರತಿಕ್ರಿಯಿಸಲು ಸಮಯ ನೀಡಿ, ಚಿತ್ರ/ಸಂಕೇತಗಳನ್ನು ಬಳಸಿ, ಸಣ್ಣ ಪ್ರಯತ್ನಗಳನ್ನೂ ಮೆಚ್ಚಿಸಿ. ನಿಯಮಿತ ಅಭ್ಯಾಸದಿಂದ ಸಂವಹನ ಕೌಶಲ್ಯ ಉತ್ತಮವಾಗುತ್ತದೆ.",
        "bn": "যোগাযোগ উন্নত করতে সহজ ভাষা ব্যবহার করুন, শিশুকে উত্তর দেওয়ার সময় দিন, ছবি/ইশারা ব্যবহার করুন, ছোট চেষ্টাকেও প্রশংসা করুন। নিয়মিত অনুশীলনে যোগাযোগ দক্ষতা বাড়ে।"
    }
}

localized_fallback = {
    "hi": "कृपया ऑटिज्म से जुड़ा प्रश्न पूछें, जैसे: लक्षण, जांच, इलाज या संवाद कैसे सुधारें।",
    "ta": "ஆட்டிசம் தொடர்பான கேள்வி கேளுங்கள்: அறிகுறிகள், கண்டறிதல், சிகிச்சை அல்லது தொடர்பு மேம்பாடு.",
    "te": "దయచేసి ఆటిజం సంబంధిత ప్రశ్న అడగండి: లక్షణాలు, నిర్ధారణ, చికిత్స లేదా కమ్యూనికేషన్.",
    "ml": "ദയവായി ഓട്ടിസം സംബന്ധിച്ച ചോദ്യം ചോദിക്കൂ: ലക്ഷണങ്ങൾ, നിർണയം, ചികിത്സ, ആശയവിനിമയം.",
    "kn": "ದಯವಿಟ್ಟು ಆಟಿಸಂ ಸಂಬಂಧಿತ ಪ್ರಶ್ನೆ ಕೇಳಿ: ಲಕ್ಷಣಗಳು, ನಿರ್ಣಯ, ಚಿಕಿತ್ಸೆ ಅಥವಾ ಸಂವಹನ.",
    "bn": "অনুগ্রহ করে অটিজম-সম্পর্কিত প্রশ্ন করুন: লক্ষণ, নির্ণয়, চিকিৎসা বা যোগাযোগ।"
}


def normalize_text(text):
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def keyword_score(messages, keywords):
    """Return overlap score between user messages and keyword tokens."""
    message_tokens = set()
    for msg in messages:
        tokens = [t for t in re.split(r"[^\w]+", msg) if len(t) > 2]
        message_tokens.update(tokens)

    score = 0
    for kw in keywords:
        kw_norm = normalize_text(kw)
        if not kw_norm:
            continue
        if any(kw_norm in msg for msg in messages):
            score += 5
            continue

        kw_tokens = [t for t in re.split(r"[^\w]+", kw_norm) if len(t) > 2]
        overlap = sum(1 for t in kw_tokens if t in message_tokens)
        if overlap >= 2:
            score += 3
        elif overlap == 1:
            score += 1
    return score


def build_topic_score(searchable_messages, topic, info):
    """Score a topic using weighted phrase and token matches."""
    topic_keywords = []
    for key, values in info.items():
        if key.startswith("keywords_") and isinstance(values, list):
            topic_keywords.extend(values)

    # Generic terms that should not dominate intent.
    weak_terms = {
        "autism", "autistic", "asd", "help", "tips", "advice",
        "support", "query", "question", "topic"
    }

    normalized_keywords = []
    for kw in topic_keywords:
        kw_norm = normalize_text(kw)
        if not kw_norm:
            continue
        if kw_norm in weak_terms:
            continue
        if len(kw_norm) <= 2:
            continue
        normalized_keywords.append(kw_norm)

    phrase_score = 0
    token_score = 0
    for kw in normalized_keywords:
        if any(kw in msg for msg in searchable_messages):
            # Longer phrases are stronger intent signals.
            phrase_score += 8 if len(kw.split()) >= 2 else 4
            continue

        kw_tokens = [t for t in re.split(r"[^\w]+", kw) if len(t) > 2 and t not in weak_terms]
        if not kw_tokens:
            continue

        overlap_hits = 0
        for msg in searchable_messages:
            msg_tokens = set(t for t in re.split(r"[^\w]+", msg) if len(t) > 2)
            overlap_hits = max(overlap_hits, sum(1 for t in kw_tokens if t in msg_tokens))

        if overlap_hits >= 2:
            token_score += 3
        elif overlap_hits == 1:
            token_score += 1

    # Slightly demote broad intro topic to avoid catching all queries.
    if topic == "what_is_autism":
        phrase_score = max(0, phrase_score - 4)

    return phrase_score + token_score


def localize_text(text, lang):
    """Translate response text to selected language when needed."""
    if not text or lang == "en":
        return text
    try:
        return translate_text_sync(text, "en", lang)
    except Exception:
        return text

def translate_text_sync(text, src_lang, dest_lang):
    try:
        translator = Translator()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(translator.translate(text, src=src_lang, dest=dest_lang))
            return result.text
        finally:
            loop.close()
    except Exception as e:
        print(f"Translation error: {e}")
        return text

# Comprehensive autism knowledge base with multilingual keywords
autism_info = {
    "what_is_autism": {
        "keywords_en": ["what is autism", "autism meaning", "autism kya hai", "autism explained", "define autism", "asd", "autistic"],
        "keywords_hi": ["ऑटिज्म क्या है", "ऑटिज्म का मतलब", "ASD क्या है", "ऑटिस्टिक"],
        "keywords_ta": ["ஆட்டிசம் என்றால் என்ன", "ஆட்டிசம் பொருள்", "ஆசுடிசம்"],
        "keywords_te": ["ఆటిజం అంటే ఏమిటి", "ASD ఏమిటి"],
        "keywords_ml": ["ആടിസം എന്താണ്", "ആടിസത്തിന്റെ അര്ത്ഥം"],
        "keywords_kn": ["ಆಟಿಸಂ ಎಂದರೆಯಾದರೂ", "ಆಟಿಸಂ ಅರ್ಥ"],
        "keywords_bn": ["অটিজম কী", "অটিজমের অর্থ", "ASD কী"],
        "response": "Autism Spectrum Disorder (ASD) is a developmental condition affecting communication and behavior. Key points: Autism is a spectrum with different strengths and challenges. It affects social communication and behavior. Symptoms appear in early childhood. There's no cure, but early intervention helps. With support, autistic individuals can thrive."
    },
    "symptoms": {
        "keywords_en": ["symptoms", "signs", "characteristics", "behaviors", "autism symptoms", "autism signs", "red flags", "warning signs", "what are symptoms"],
        "keywords_hi": ["लक्षण", "निशान", "ऑटिज्म के लक्षण", "ऑटिज्म के निशान", "लक्षण क्या हैं", "बच्चे में ऑटिज्म"],
        "keywords_ta": ["அறிகுறிகள்", "ஆட்டிசம் அறிகுறிகள்", "குழந்தைக்கு ஆட்டிசம்", "என்ன அறிகுறிகள்"],
        "keywords_te": ["లక్షణాలు", "ఆటిజం లక్షణాలు", "బిడ్డలో ఆటిజం"],
        "keywords_ml": ["ലക്ഷണങ്ങൾ", "ആടിസത്തിന്റെ ലക്ഷണങ്ങൾ", "കുട്ടിയിലെ ലക്ഷണങ്ങൾ"],
        "keywords_kn": ["ಲಕ್ಷಣಗಳು", "ಆಟಿಸಂ ಲಕ್ಷಣಗಳು", "ಮಕ್ಕಳಲ್ಲಿ ಆಟಿಸಂ"],
        "keywords_bn": ["লক্ষণ", "অটিজমের লক্ষণ", "শিশুর অটিজমের লক্ষণ", "কী কী লক্ষণ"],
        "response": "Common signs: Social: Limited eye contact, doesn't respond to name, difficulty understanding feelings, delayed speech, repeats words. Behavior: Repetitive movements, insists on same routines, intense interests, unusual reactions to sounds/textures. Early signs appear 12-18 months."
    },
    "diagnosis": {
        "keywords_en": ["diagnosis", "diagnose", "test", "evaluation", "autism test", "screening", "doctor", "how to diagnose"],
        "keywords_hi": ["निदान", "पहचान", "जांच", "ऑटिज्म की जांच", "डॉक्टर", "परीक्षण", "मूल्यांकन"],
        "keywords_ta": ["அறுத்திப்படுத்தல்", "பரிசோதனை", "ஆட்டிசம் பரிசோதனை", "மதிப்பீடு", "மருத்துவர்"],
        "keywords_te": ["diagnose", "परीक्षण", "ఆటిజం నిర్ధారణ", "डॉक्टर"],
        "keywords_ml": ["രോഗനിര്യാതനം", "പരിശോധന", "ആടിസം കണ്ടെത്തൽ", "ഡോക്ടർ"],
        "keywords_kn": ["ನಿರ್ಧರಿಸು", "ಪರೀಕ್ಷೆ", "ಆಟಿಸಂ ಪತ್ತೆ", "ವೈದ್ಯರು"],
        "keywords_bn": ["নির্ণয়", "পরীক্ষা", "অটিজম নির্ণয়", "ডাক্তার", "মূল্যায়ন"],
        "response": "Diagnosis process: 1) Developmental screening at 18 & 24 months. 2) Comprehensive evaluation by developmental pediatrician, child psychologist, speech therapist, occupational therapist. Includes observation, parent interviews, standardized tests. Early diagnosis leads to better outcomes!"
    },
    "treatment": {
        "keywords_en": ["treatment", "therapy", "treat", "cure", "help", "autism treatment", "autism therapy", "intervention", "healing"],
        "keywords_hi": ["इलाज", "उपचार", "थेरेपी", "ऑटिज्म का इलाज", "उपचार कैसे करें", "सुधार"],
        "keywords_ta": ["சிகிச்சை", "சிகிச்சை முறை", "ஆட்டிசம் சிகிச்சை", "குணப்படுத்த"],
        "keywords_te": ["చికిత్స", "ఆటిజం చికిత్స", "ఎలా కురుపు"],
        "keywords_ml": ["ചികിത്സ", "ആടിസം ചികിത്സ", "എങ്ങനെ സുഖപ്പെടുത്താം"],
        "keywords_kn": ["ಚಿಕಿತ್ಸೆ", "ಆಟಿಸಂ ಚಿಕಿತ್ಸೆ", "ಗುಣಪಡಿಸು"],
        "keywords_bn": ["চিকিৎসা", "থেরাপি", "অটিজমের চিকিৎসা", "সুস্থ করা"],
        "response": "Effective treatments: Behavioral: ABA therapy, Floortime, RDI. Therapies: Speech therapy, Occupational therapy, Physical therapy, Social skills training. Medical: Medications for specific symptoms. Other: Music therapy, Animal-assisted therapy. Early intervention is crucial!"
    },
    "communication": {
        "keywords_en": ["communication", "talk", "speak", "language", "speech", "how to communicate", "nonverbal", "verbal", "sign language"],
        "keywords_hi": ["संवाद", "बात", "भाषा", "बोलना", "गैर-मौखिक", "संकेत भाषा", "बात कैसे करें"],
        "keywords_ta": ["தொடர்பு", "பேச்சு", "மொழி", "பேசமுடியாத", "சின்னம் மொழி"],
        "keywords_te": ["Communication", "मాట", "భాష", "মాట లేని", "Signal భాష"],
        "keywords_ml": ["ആശയവിനിമയം", "സംസാരിക്കുക", "ഭാഷ", "വാക്കില്ലാത്ത"],
        "keywords_kn": ["ಸಂವಹನ", "ಮಾತನಾಡು", "ಭಾಷೆ", "ಮಾತಿಲ್ಲದ", "ಸಂಕೇತ ಭಾಷೆ"],
        "keywords_bn": ["যোগাযোগ", "কথা", "ভাষা", "কথা বলতে পারে না", "চিহ্ন ভাষা"],
        "response": "Improving communication: For verbal: Use simple clear sentences, give time to respond, be patient, follow their interests, avoid sarcasm. For non-verbal: Use picture cards, sign language, communication devices, pointing and gestures. Praise any communication attempt!"
    },
    "sensory": {
        "keywords_en": ["sensory", "sensory issues", "sensory processing", "sound sensitive", "touch sensitive", "light sensitive", "textures", "sensory overload"],
        "keywords_hi": ["संवेदी", "संवेदी समस्याएं", "आवाज के प्रति संवेदनशील", "छूने के प्रति संवेदनशील", "रोशनी से परेशान"],
        "keywords_ta": ["அறிவுசார்", "அறிவுசார் சிக்கல்", "ஒலிக்கு حساس", "தொடுவதற்கு حساس"],
        "keywords_te": ["sensor", "sensor issues", "శబ్దానికి حساس", "తాకుడుకు حساس"],
        "keywords_ml": ["സംവേദനാത്മക", "സംവേദന പ്രശ്നങ്ങൾ", "ശബ്ദത്തോട് حساس"],
        "keywords_kn": ["ಸಂವೇದನಾತ್ಮಕ", "ಸಂವೇದನಾ ಸಮಸ್ಯೆಗಳು", "ಶಬ್ದಕ್ಕೆ ಸಂವೇದನಾಶೀಲ"],
        "keywords_bn": ["ইন্দ্রিয়", "ইন্দ্রিয় সমস্যা", "শব্দের প্রতি সংবেদনশীল", "স্পর্শে সংবেদনশীল"],
        "response": "Managing sensory issues: Common sensitivities: sounds, textures, lights. Strategies: Create calm sensory space, use noise-canceling headphones, provide weighted blankets, gradual exposure therapy. Occupational therapist can help with personalized strategies."
    },
    "behavior": {
        "keywords_en": ["behavior", "tantrum", "meltdown", "aggressive", "outburst", "problem behavior", "challenging behavior", "self-harm"],
        "keywords_hi": ["व्यवहार", "गुस्सा", "झुंझलाहट", "अटैक", "आक्रामक", "खुद को नुकसान", "मारना"],
        "keywords_ta": ["நடத்தை", "கோபம்", "கதறல்", "ஆகிரime", "தன்னைத்தான் காயப்படுத்த"],
        "keywords_te": ["behavior", "peshavior", "ఆವೇಶం", "బಲం", "తాము hurt"],
        "keywords_ml": ["പെരുമാറ്റം", "കോപം", "അസ്വസ്ഥത", "ആക്രമണം"],
        "keywords_kn": ["ನಡವಳಿಕೆ", "ಕೋಪ", "ಸಿಡುಬು", "ದಾಳಿ", "ತಾವನ್ನು ಗಾಯಗೊಳಿಸಿಕೊಳ್ಳುವುದು"],
        "keywords_bn": ["আচরণ", "রাগ", "মেল্টডাউন", "আক্রমণাত্মক", "নিজেকে আঘাত"],
        "response": "Handling behaviors: Understand causes: communication attempts, sensory overload, frustration, medical issues. Prevention: consistent routines, visual schedules, warnings before changes. During meltdown: stay calm, remove from triggers, give space. After: discuss calmly, teach alternative skills."
    },
    "education": {
        "keywords_en": ["education", "school", "learn", "teacher", "classroom", "iep", "special education", "inclusion", "mainstream"],
        "keywords_hi": ["शिक्षा", "स्कूल", "पढ़ाई", "शिक्षक", "विशेष शिक्षा", "IEP", "सामान्य शिक्षा"],
        "keywords_ta": ["கல்வி", "பள்ளி", "அம்மா", "ஆசிரியர்", "சிறப்பு கல்வி"],
        "keywords_te": ["shiksham", "school", "teacher", "చదువు", "पాఠశాల", "विशेष Shiksham"],
        "keywords_ml": ["വിദ്യാഭ്യാസം", "സ്കൂൾ", "അദ്ധ്യാപകൻ", "പ്രത്യേക വിദ്യാഭ്യാസം"],
        "keywords_kn": ["ಶಿಕ್ಷಣ", "ಶಾಲೆ", "ಶಿಕ್ಷಕ", "ವಿಶೇಷ ಶಿಕ್ಷಣ", "IEP"],
        "keywords_bn": ["শিক্ষা", "স্কুল", "শিক্ষক", "বিশেষ শিক্ষা", "IEP"],
        "response": "Education options: Regular school with support, Special education school, Autism-specific school, Home schooling. IEP: Legal document with customized goals, accommodations, regular reviews. Services: Special ed teacher, speech therapy, OT, aides. Tips: Start small, communicate with teachers, use visual supports."
    },
    "family": {
        "keywords_en": ["family", "parent", "parents", "support", "sibling", "family support", "caregiver", "stress", "marriage"],
        "keywords_hi": ["परिवार", "माता-पिता", "सहायता", "भाई-बहन", "परिवार का समर्थन", "तनाव", "शादी"],
        "keywords_ta": ["குடும்பம்", "பெற்றோர்", "ஆதரவு", "உடன் பிறந்தோர்", "குடும்ப ஆதரவு"],
        "keywords_te": ["family", "parents", "support", "తలைയർ", "কুটুம"],
        "keywords_ml": ["കുടുംബം", "രക്ഷിതാക്കൾ", "പിന്തുണ", "സഹോദരങ്ങൾ"],
        "keywords_kn": ["ಕುಟುಂಬ", "ಪೋಷಕರು", "ಬೆಂಬಲ", "ಸಹೋದರ", "ಕುಟುಂಬ ಒತ್ತಡ"],
        "keywords_bn": ["পরিবার", "বাবা-মা", "সহায়তা", "ভাই-বোন", "পরিবারের চাপ"],
        "response": "Family support: For parents: It's okay to feel overwhelmed, take breaks (respite care), stay connected with partner, seek counseling. For siblings: Involve in therapy, explain autism simply, give one-on-one time. Build support network: join autism groups, connect with other families."
    },
    "daily_skills": {
        "keywords_en": ["daily living", "self care", "toilet training", "eating", "sleeping", "dressing", "brushing teeth", "bathing", "routine", "independence"],
        "keywords_hi": ["दैनिक जीवन", "स्व-देखभाल", "शौचालय प्रशिक्षण", "खाना", "नींद", "कपड़े पहनना", "दांत साफ करना"],
        "keywords_ta": ["தினசரி வாழ்க்கை", "சுய பராமரிப்பு", "கழிப்பறை பயிற்சி", "சாப்பிட", "தூக்கம்", "உடை"],
        "keywords_te": ["daily life", "self care", " toileting", "bhojanam", "Nidra", "veshtu"],
        "keywords_ml": ["ദൈനംനിത്തിരുവാതിര", "സ്വയം പരിചരണം", "ശുചിത്വം", "ഭക്ഷണം"],
        "keywords_kn": ["ದೈನಂದಿನ ಜೀವನ", "ಸ್ವ-ಆರೈಕೆ", "ಶೌಚಾಲಯ ತರಬೇತಿ", "ತಿನ್ನುವುದು", "ನಿದ್ರೆ"],
        "keywords_bn": ["দৈনন্দিন জীবন", "সেলফ কেয়ার", "টয়লেট ট্রেনিং", "খাওয়া", "ঘুম", "পোশাক"],
        "response": "Daily skills: Toilet training: Wait for readiness (3-4 years), use visual schedules, be patient, reward successes. Eating: Introduce foods gradually, don't force, make mealtimes positive. Sleeping: Consistent routine, cool dark room, avoid screens. Dressing: Practice buttons, allow extra time."
    },
    "sleep": {
        "keywords_en": ["sleep", "sleeping", "insomnia", "sleep problems", "can't sleep", "night waking", "sleep training", "bedtime"],
        "keywords_hi": ["नींद", "नींद नहीं आती", "नींद की समस्या", "रात को जागना", "सुलाने के तरीके"],
        "keywords_ta": ["தூக்கம்", "தூக்கம் வராது", "தூக்கப் பிரச்சினை", "இரவில் எழும்ப"],
        "keywords_te": ["Nidra", "sleep", "Nidra lagavale", "ratri jagrata"],
        "keywords_ml": [" uyarnnu", "ഉറക്കം", "ഉറക്കത്തിന്റെ പ്രശ്നങ്ങൾ"],
        "keywords_kn": ["ನಿದ್ರೆ", "ನಿದ್ರೆ ಬರದಿರುವಿಕೆ", "ನಿದ್ರಾ ಸಮಸ್ಯೆಗಳು", "ರಾತ್ರಿ ಏಳಿಬರುವುದು"],
        "keywords_bn": ["ঘুম", "ঘুম আসছে না", "ঘুমের সমস্যা", "রাতে জেগে থাকা"],
        "response": "Sleep problems: Common issues: difficulty falling asleep, frequent night waking, early morning waking. Solutions: Consistent bedtime routine, cool dark quiet room, white noise, weighted blanket, avoid screens before bed. Bedtime: Calm activities, bath, story, dim lights. Consult doctor if persistent."
    },
    "eating": {
        "keywords_en": ["eating", "food", "picky eater", "food aversion", "eating problems", "nutrition", "weight", "diet", "refuses food"],
        "keywords_hi": ["खाना", "भोजन", "भूख नहीं लगता", "खाने की समस्या", "वजन", "आहार"],
        "keywords_ta": ["சாப்பிட", "உணவு", "அதிகம் தோத", "உணவு பிரச்சினை"],
        "keywords_te": ["bhojanam", "aharam", "tinadam", "vikarthi"],
        "keywords_ml": ["ഭക്ഷണം", "കഴിക്കുന്നത്", "ഭക്ഷണ പ്രശ്നങ്ങൾ"],
        "keywords_kn": ["ತಿನ್ನುವುದು", "ಆಹಾರ", "ತಿನ್ನುವ ಸಮಸ್ಯೆಗಳು", "ಪೋಷಣೆ"],
        "keywords_bn": ["খাওয়া", "খাবার", "খাবার সমস্যা", "পুষ্টি", "ওজন"],
        "response": "Eating issues: Common: limited food preferences, food jags, sensory issues with textures. Solutions: Introduce foods gradually, don't force, make food fun (cut shapes), involve in cooking, praise trying. Nutrition tips: Focus on what they DO eat, multiple small meals, smoothies help, consult nutritionist."
    },
    "social_skills": {
        "keywords_en": ["social skills", "social interaction", "friends", "playing", "share", "take turns", "make friends", "socialize", "play date"],
        "keywords_hi": ["सामाजिक कौशल", "दोस्त", "खेलना", "बांटना", "बारी", "दोस्त बनाना", "मिलकर खेलना"],
        "keywords_ta": ["சமூக திறன்கள்", "நண்பர்கள்", "விளையாட", "பகிர", "மாற்ற"],
        "keywords_te": ["social skills", "friends", "chusko", "saeratanam"],
        "keywords_ml": ["സാമൂഹിക കഴിവുകൾ", "സുഹൃത്തുക്കൾ", "കളിക്കുക", "പങ്കിടാന്‍"],
        "keywords_kn": ["ಸಾಮಾಜಿಕ ಕೌಶಲ್ಯಗಳು", "ಸ್ನೇಹಿತರು", "ಆಡುವುದು", "ಹಂಚಿಕೆ"],
        "keywords_bn": ["সামাজিক দক্ষতা", "বন্ধু", "খেলা", "শেয়ার", "বন্ধু করা"],
        "response": "Building social skills: Teach: taking turns, sharing, personal space, reading social cues. Strategies: play-based learning, social stories, role-playing, video modeling, group activities. Tips: Start one-on-one, use special interests, praise effort, don't force interaction, find neurodiverse-friendly groups."
    },
    "future": {
        "keywords_en": ["future", "adult", "independent", "job", "work", "driving", "college", "marriage", "transition", "adult services", "guardianship"],
        "keywords_hi": ["भविष्य", "वयस्क", "स्वतंत्र", "नौकरी", "ड्राइविंग", "कॉलेज", "शादी", "संक्रमण"],
        "keywords_ta": ["எதிர்காலம்", "வயது", "சுயாதீனமான", "வேலை", "திருமணம்"],
        "keywords_te": ["future", "adult", "job", "vyakt", "mantri", "vivaham"],
        "keywords_ml": ["ഭാവി", "മുതിരൻ", "ജോലി", "വിവാഹം"],
        "keywords_kn": ["ಭವಿಷ್ಯ", "ವಯಸ್ಸಾದ", "ಕೆಲಸ", "ಮದುವೆ", "ಸ್ವಾತಂತ್ರ್ಯ"],
        "keywords_bn": ["ভবিষ্যত", "প্রাপ্তবয়স্ক", "কাজ", "বিয়ে", "স্বাধীনতা"],
        "response": "Planning future: Independent living: self-care, money management, cooking, public transport. Education/work: vocational training, college with support, job coaching. Legal: guardianship, power of attorney, special needs trusts, disability benefits. Healthcare: find adult doctors, understand insurance. Start planning in teen years!"
    },
    "tips": {
        "keywords_en": ["tips", "advice", "help", "suggestions", "guidance", "how to help", "what to do", "strategies", "techniques"],
        "keywords_hi": ["सुझाव", "सलाह", "मदद", "क्या करें", "गाइड", "उपाय", "तरीके"],
        "keywords_ta": ["உதவிக்குறிப்பு", "அறிவுரை", "என்ன செய்ய வேண்டும்"],
        "keywords_te": ["suggestion", "advice", "help", "em chestunavu"],
        "keywords_ml": ["ഉപദേശം", "സഹായം", "എന്തുചെയ്യണം"],
        "keywords_kn": ["ಸಲಹೆ", "ಸಹಾಯ", "ಏನು ಮಾಡಬೇಕು"],
        "keywords_bn": ["টিপস", "পরামর্শ", "সাহায্য", "কী করব"],
        "response": "General tips: Daily: Use visual schedules, give warnings before changes, keep routines consistent, use positive reinforcement. Communication: Get on their level, use clear simple language, give wait time, listen actively. Behavior: Stay calm, be consistent, pick battles, celebrate wins. Self-care: Take breaks, connect with other parents, ask for help."
    },
    "therapies": {
        "keywords_en": ["therapies", "different therapies", "types of therapy", "ot", "pt", "speech", "occupational therapy", "physical therapy"],
        "keywords_hi": ["विभिन्न थेरेपी", "ओटी", "पीटी", "स्पीच थेरेपी", "आकुपेशनल थेरेपी"],
        "keywords_ta": ["சிகிச்சைகள்", "OT", "PT", "ஆக்குபேஷனல் தெரபி"],
        "keywords_te": ["therapies", "OT", "PT", "speech therapy"],
        "keywords_ml": ["ചികിത്സകൾ", "OT", "PT", "speech"],
        "keywords_kn": ["ಚಿಕಿತ್ಸೆಗಳು", "OT", "PT", "ಭಾಷಾ ಚಿಕಿತ್ಸೆ"],
        "keywords_bn": ["থেরাপি", "OT", "PT", "স্পিচ থেরাপি"],
        "response": "Therapies overview: Speech-Language Therapy: improves communication, speech sounds, language comprehension. Occupational Therapy: fine motor, daily living, sensory integration. Physical Therapy: gross motor, balance, coordination. Behavioral: ABA, Floortime, Social Thinking. Team approach works best!"
    }
}

greetings_map = {
    "en": ["hello", "hi", "hey", "greetings", "good morning"],
    "hi": ["नमस्ते", "हेलो", "हाय", "नमस्कार"],
    "ta": ["வணக்கம்", "ஹேலோ"],
    "te": ["namaste", "హలो"],
    "ml": ["നമസ്കാരം", "ഹലോ"],
    "kn": ["ನಮಸ್ಕಾರ", "ಹಲೋ"],
    "bn": ["নমস্কার", "হ্যালো"]
}

thanks_map = {
    "en": ["thank", "thanks", "appreciate"],
    "hi": ["धन्यवाद", "शुक्रिया", "आभार"],
    "ta": ["நன்றி"],
    "te": ["ధన్యవాదాలు"],
    "ml": ["നന്ദി"],
    "kn": ["ಧನ್ಯವಾದಗಳು"],
    "bn": ["ধন্যবাদ"]
}

def get_response(user_message, lang, original_message=None):
    user_message_lower = normalize_text(user_message)
    original_message_lower = normalize_text(original_message)
    searchable_messages = [user_message_lower]
    if original_message_lower and original_message_lower != user_message_lower:
        searchable_messages.append(original_message_lower)
    
    # Check greeting
    for _lang_code, greetings in greetings_map.items():
        if any(greet.lower() in msg for msg in searchable_messages for greet in greetings):
            return localize_text(
                "Hello! I'm here to help parents of autistic children. Ask me about symptoms, diagnosis, treatment, communication, education, behavior, or any autism-related topic.",
                lang
            )
    
    # Check thanks
    for _lang_code, thanks_words in thanks_map.items():
        if any(thank.lower() in msg for msg in searchable_messages for thank in thanks_words):
            return localize_text("You're welcome! Feel free to ask more questions about autism.", lang)
    
    # Match keywords
    matched_topic = None
    best_score = 0
    for topic, info in autism_info.items():
        score = build_topic_score(searchable_messages, topic, info)
        if score > best_score:
            best_score = score
            matched_topic = topic

    # Avoid weak accidental matches.
    if best_score < 4:
        matched_topic = None
    
    if not matched_topic:
        autism_related = ["autism", "autistic", "asd", "spectrum", "आಟಿಸം", "ആടിസം", "ఆటిజం", "অটিজম", "ஆட்டிசம்"]
        if any(word in msg for msg in searchable_messages for word in autism_related):
            return localize_text(
                "That's a great question about autism! Ask about: symptoms, diagnosis, treatment, communication, sensory issues, education, behavior, daily skills, sleep, eating, social skills, family support, future planning, or general tips.",
                lang
            )
        else:
            if lang in localized_fallback:
                return localized_fallback[lang]
            return localize_text(
                "I'm specifically designed to help with autism-related questions. Please ask queries related to Autism only. I can help with: symptoms, treatment, communication, education, behavior, family support, and more.",
                lang
            )
    
    response = autism_info.get(matched_topic, {}).get("response", "")
    if matched_topic in localized_responses and lang in localized_responses[matched_topic]:
        response = localized_responses[matched_topic][lang]
    if response:
        followups = {
            "hi": "क्या आप इस विषय पर और जानकारी चाहते हैं?",
            "ta": "இந்த தலைப்பில் இன்னும் தகவல் வேண்டுமா?",
            "te": "ఈ విషయంపై మరిన్ని వివరాలు కావాలా?",
            "ml": "ഈ വിഷയത്തിൽ കൂടുതൽ വിവരങ്ങൾ വേണമോ?",
            "kn": "ಈ ವಿಷಯದ ಬಗ್ಗೆ ಇನ್ನಷ್ಟು ಮಾಹಿತಿ ಬೇಕೇ?",
            "bn": "এই বিষয়ে আরও তথ্য চান কি?"
        }
        if lang != "en" and matched_topic not in localized_responses:
            response = localize_text(response, lang)
        response += "\n\n" + followups.get(lang, localize_text("Would you like more information on this topic?", lang))
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send_message", methods=["POST"])
def send_message():
    user_message = request.json.get("message")
    session_id = request.json.get("session_id")
    lang = request.json.get("lang", "en")

    user_message_en = user_message
    if lang != "en":
        try:
            user_message_en = translate_text_sync(user_message, lang, "en")
        except Exception as e:
            print(f"Translation error: {e}")
            user_message_en = user_message

    try:
        reply = get_response(user_message_en, lang, original_message=user_message)

        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
