import os
import time
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from chatbot.rag_pipeline import retrieve_context
from chatbot.prompt_template import (
    HOME_PROMPT,
    GENERAL_AGRICULTURE_PROMPT,
    CONTEXT_PROMPT_TEMPLATE
)

load_dotenv()

def get_client():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key or not api_key.strip():
        return None
    try:
        return OpenAI(
            base_url = "https://openrouter.ai/api/v1",
            api_key  = api_key.strip()
        )
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {e}")
        return None

MODEL       = "google/gemma-3-4b-it:free"
MAX_HISTORY = 5

_conversation_histories = {}
_disease_catalog = None


# ── Load Disease Metadata Catalog ─────────────────────────────────────────────
def get_disease_catalog() -> dict:
    global _disease_catalog
    if _disease_catalog is None:
        try:
            base_dir = Path(__file__).resolve().parent.parent
            path = base_dir / "final_model" / "disease_classes.json"
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    _disease_catalog = json.load(f)
            else:
                _disease_catalog = {}
        except Exception as e:
            print(f"Error loading disease catalog: {e}")
            _disease_catalog = {}
    return _disease_catalog


# ── Pick system prompt based on page ──────────────────────────────────────────
def get_system_prompt(prediction_context: dict) -> str:
    if not prediction_context:
        return HOME_PROMPT  # home page — no context = website guide mode

    feature = prediction_context.get("feature", "")

    if feature in ["crop_recommendation", "yield_prediction", "soil_health", "disease_detection"]:
        return GENERAL_AGRICULTURE_PROMPT  # all feature pages = agriculture expert

    return HOME_PROMPT


# ── Format prediction context for prompt ──────────────────────────────────────
def get_prediction_context_text(prediction_context: dict) -> str:
    if not prediction_context:
        return "None"

    feature = prediction_context.get("feature", "")

    if feature == "crop_recommendation":
        crop = prediction_context.get("crop", "Unknown")
        return f"Crop Recommendation Result: Recommended crop is {crop}"

    elif feature == "yield_prediction":
        crop      = prediction_context.get("crop", "Unknown")
        season    = prediction_context.get("season", "Unknown")
        yield_val = prediction_context.get("yield", "Unknown")
        return f"Yield Prediction Result: {crop} in {season} season — predicted yield is {yield_val} tonnes/hectare"

    elif feature == "soil_health":
        fertilizer = prediction_context.get("fertilizer", "Unknown")
        return f"Soil Health Result: Recommended fertilizer is {fertilizer}"

    elif feature == "disease_detection":
        crop     = prediction_context.get("crop", "Unknown")
        disease  = prediction_context.get("disease", "Unknown")
        severity = prediction_context.get("severity", "Moderate")
        pathogen = prediction_context.get("pathogen_type", "Fungal / Physiological")
        org      = prediction_context.get("organic_treatment", "")
        chem     = prediction_context.get("chemical_treatment", "")
        prev     = prediction_context.get("prevention", "")
        return (
            f"Plant Disease Scanner Result:\n"
            f"- Crop: {crop}\n"
            f"- Disease Diagnosis: {disease}\n"
            f"- Pathogen Classification: {pathogen}\n"
            f"- Severity Level: {severity}\n"
            f"- Organic Remedy: {org}\n"
            f"- Chemical Treatment: {chem}\n"
            f"- Prevention Protocol: {prev}"
        )

    return "None"


# ── Smart Agronomic Fallback Responder ────────────────────────────────────────
def generate_expert_fallback(message: str, prediction_context: dict = None) -> dict:
    """
    Intelligent agronomic advisory engine that generates domain-accurate,
    professional agricultural guidance even when an LLM API key is not configured.
    """
    catalog = get_disease_catalog()
    msg_lower = (message or "").lower()

    # 1. Prediction Context: Disease Detection
    if prediction_context and prediction_context.get("feature") == "disease_detection":
        crop = prediction_context.get("crop") or "Crop"
        disease = prediction_context.get("disease") or "Diagnosed Condition"
        severity = prediction_context.get("severity") or "Moderate"
        pathogen = prediction_context.get("pathogen_type") or "Fungal / Physiological"
        organic = prediction_context.get("organic_treatment") or ""
        chemical = prediction_context.get("chemical_treatment") or ""
        prevention = prediction_context.get("prevention") or ""

        # Enrich from catalog if details are sparse
        matched_item = None
        for item in catalog.values():
            if item.get("disease_name", "").lower() == disease.lower() or (crop.lower() in item.get("crop", "").lower() and disease.lower() in item.get("disease_name", "").lower()):
                matched_item = item
                break

        if matched_item:
            pathogen = matched_item.get("pathogen_type", pathogen)
            severity = matched_item.get("severity", severity)
            organic = matched_item.get("organic_treatment", organic)
            chemical = matched_item.get("chemical_treatment", chemical)
            prevention = matched_item.get("prevention", prevention)

        is_healthy = "healthy" in disease.lower() or "healthy" in severity.lower()

        if is_healthy:
            reply = (
                f"### 🌿 Diagnostic Report: Healthy {crop} Foliage\n\n"
                f"**Status**: Disease-Free Leaf Tissue  \n"
                f"**Canopy Health**: Normal chlorophyll density with intact vascular structure.\n\n"
                f"#### 🌾 Maintenance & Preventive Schedule:\n"
                f"1. **Nutrient Balance**: Maintain scheduled organic compost (e.g., vermicompost or well-aged farmyard manure) to sustain natural systemic resistance.\n"
                f"2. **Irrigation Stewardship**: Water early in the morning at the root zone rather than overhead spraying to prevent fungal spore germination.\n"
                f"3. **Regular Scouting**: Perform weekly inspections on the undersides of lower leaves for early pest or rust signs.\n\n"
                f"*(💡 CropPulse Agronomic Diagnostic Engine. To enable interactive open-ended LLM conversations with Gemma, add your free `OPENROUTER_API_KEY` in environment variables.)*"
            )
        else:
            reply = (
                f"### 🩺 Plant Pathology Advisory: {disease}\n\n"
                f"**Host Crop**: {crop}  \n"
                f"**Pathogen Classification**: {pathogen}  \n"
                f"**Observed Severity**: {severity}\n\n"
                f"#### 🗓️ Recommended Treatment Schedule:\n"
                f"1. **Phase 1: Immediate Field Sanitation (Days 1–3)**\n"
                f"   - **Irrigation Adjustment**: Immediately suspend overhead sprinkler irrigation; switch to drip or furrow watering to keep the foliage completely dry.\n"
                f"   - **Canopy Sanitation**: For garden beds and small acreage, hand-prune severely blighted lower leaves touching damp soil. Safely destroy or deeply bury infected foliage to halt spore splash.\n"
                f"2. **Phase 2: Targeted Remedial Application (Days 3–7)**\n"
                f"   - **Organic / Biological**: {organic if organic else 'Apply bio-fungicides based on Bacillus subtilis or copper soap spray across upper and lower leaf surfaces.'}\n"
                f"   - **Chemical Treatment**: {chemical if chemical else 'Apply systemic protective fungicides (such as Azoxystrobin, Mancozeb, or Propiconazole) following manufacturer dosage guidelines.'}\n"
                f"3. **Phase 3: Recovery Scouting & Monitoring (Days 10–14)**\n"
                f"   - Re-inspect newly emerging flushes and the upper canopy. If high humidity and temperatures persist, repeat curative treatment per label instructions.\n\n"
                f"#### 🛡️ Long-Term Preventive & Field Management:\n"
                f"{prevention if prevention else '- Practice 1-2 year crop rotation with non-host species; ensure balanced potassium/nitrogen nutrition; optimize plant spacing for good airflow.'}\n\n"
                f"*(💡 CropPulse Agronomic Diagnostic Engine. To enable interactive open-ended LLM conversations with Gemma, add your free `OPENROUTER_API_KEY` in environment variables.)*"
            )
        return {"reply": reply, "sources": ["CropPulse Leaf Pathology Catalog", "Agri-Extension Management Guidelines"]}

    # 2. Prediction Context: Crop Recommendation
    if prediction_context and prediction_context.get("feature") == "crop_recommendation":
        crop = prediction_context.get("crop", "your recommended crop")
        reply = (
            f"### 🌱 Agronomic Cultivation Guide: {crop}\n\n"
            f"**Recommended Crop**: {crop} (Selected by CropPulse Machine Learning Model)\n\n"
            f"#### 🌾 Recommended Agronomic Schedule & Practices:\n"
            f"1. **Land & Seedbed Preparation**: Plough deeply to 20–25 cm followed by 2 passes of harrowing. Incorporate 8–10 tonnes/ha of well-rotted farmyard manure (FYM) to enhance aeration and water-holding capacity.\n"
            f"2. **Seed Treatment & Sowing**: Treat certified seed with *Trichoderma* or recommended seed dressing before sowing to protect against soil-borne damping-off. Observe recommended spacing to avoid crowded micro-climates.\n"
            f"3. **Nutrient Management (NPK)**: Apply full Phosphorus and Potassium as a basal dose along with 1/3rd Nitrogen at sowing. Top-dress remaining Nitrogen in 2 split doses during peak vegetative growth.\n"
            f"4. **Irrigation & Moisture**: Critical stages include early root establishment, vegetative tillering, and flowering/grain formation. Ensure good drainage during monsoon periods to prevent waterlogging.\n\n"
            f"*(💡 CropPulse Agronomic Diagnostic Engine. To enable interactive open-ended LLM conversations with Gemma, add your free `OPENROUTER_API_KEY` in environment variables.)*"
        )
        return {"reply": reply, "sources": ["CropPulse ML Advisory", "Precision Agriculture Best Practices"]}

    # 3. Prediction Context: Yield Prediction
    if prediction_context and prediction_context.get("feature") == "yield_prediction":
        crop = prediction_context.get("crop", "Crop")
        season = prediction_context.get("season", "Current")
        yield_val = prediction_context.get("yield", "optimal")
        reply = (
            f"### 📈 Yield Optimization Advisory: {crop} ({season} Season)\n\n"
            f"**Target Forecast**: {yield_val} tonnes/hectare\n\n"
            f"#### 🚜 Key Practices to Reach & Maximize Your Yield Potential:\n"
            f"1. **Plant Population Density**: Maintain uniform plant spacing without blank gaps. Re-sow or thin seedlings within 10 days of germination.\n"
            f"2. **Timed Nutrient Top-Dressing**: Split Nitrogen applications to coincide with maximum crop uptake phases. Consider foliar sprays of 1–2% water-soluble NPK (19:19:19) during pre-flowering transitions.\n"
            f"3. **Micronutrient Supplementation**: Foliar application of Zinc Sulphate (0.5%) and Borax (0.2%) can prevent flower drop and significantly improve grain/fruit test weight.\n"
            f"4. **Moisture & Weed Control**: Keep fields strictly weed-free during the first 30–45 days. Ensure adequate soil moisture during flowering and grain/fruit filling.\n\n"
            f"*(💡 CropPulse Agronomic Diagnostic Engine. To enable interactive open-ended LLM conversations with Gemma, add your free `OPENROUTER_API_KEY` in environment variables.)*"
        )
        return {"reply": reply, "sources": ["CropPulse Yield Analytics", "ICAR Crop Management Protocols"]}

    # 4. Prediction Context: Soil Health & Fertilizer
    if prediction_context and prediction_context.get("feature") == "soil_health":
        fert = prediction_context.get("fertilizer", "Recommended Fertilizer")
        reply = (
            f"### 🧪 Soil Health & Fertilizer Application Guide: {fert}\n\n"
            f"**Prescribed Amendment**: {fert}\n\n"
            f"#### 🌾 Application Method & Field Guidelines:\n"
            f"1. **Placement Technique**: Band place or incorporate basal nutrients 5–7 cm below and beside seed furrows. Avoid direct contact with germinating seeds.\n"
            f"2. **Split Application Timing**: For quick-release Nitrogenous fertilizers (such as Urea), split into 2–3 doses during peak vegetative growth rather than a single heavy dose.\n"
            f"3. **Moisture Conditions**: Always apply fertilizers when the topsoil is moist; follow with light irrigation. Avoid application immediately before anticipated heavy rainstorms to prevent runoff.\n"
            f"4. **Organic Carbon Integration**: Pair synthetic fertilizers with vermicompost, composted poultry manure, or green manuring to boost microbial activity and nutrient efficiency (NUE).\n\n"
            f"*(💡 CropPulse Agronomic Diagnostic Engine. To enable interactive open-ended LLM conversations with Gemma, add your free `OPENROUTER_API_KEY` in environment variables.)*"
        )
        return {"reply": reply, "sources": ["CropPulse Soil Advisor", "Fertilizer Management Manual"]}

    # 5. Disease Keyword Matching (even without prediction context)
    for cid, item in catalog.items():
        d_name = item.get("disease_name", "")
        raw_name = item.get("raw_name", "")
        if d_name.lower() in msg_lower or (len(d_name) > 5 and all(w in msg_lower for w in d_name.lower().split() if len(w) > 3)):
            crop = item.get("crop", "Crop")
            organic = item.get("organic_treatment", "")
            chemical = item.get("chemical_treatment", "")
            prevention = item.get("prevention", "")
            desc = item.get("description", "")
            reply = (
                f"### 🌿 Diagnostic Information: {d_name} on {crop}\n\n"
                f"**Description**: {desc}\n\n"
                f"#### 🗓️ Recommended Treatment Schedule:\n"
                f"- **Organic / Biological**: {organic}\n"
                f"- **Chemical Treatment**: {chemical}\n"
                f"- **Prevention Protocol**: {prevention}\n\n"
                f"*(💡 CropPulse Agronomic Diagnostic Engine. To enable interactive open-ended LLM conversations with Gemma, add your free `OPENROUTER_API_KEY` in environment variables.)*"
            )
            return {"reply": reply, "sources": ["CropPulse Plant Disease Catalog"]}

    # 6. Navigation Inquiries
    if any(k in msg_lower for k in ["disease", "scan", "leaf", "blight", "spot", "rust", "rot", "sick plant", "photo"]):
        reply = (
            "You can diagnose plant leaf diseases and get tailored treatment schedules by visiting the "
            "**[Crop Disease Detection](/disease-detection)** page! Simply upload a photo or capture a live image with your camera."
        )
        return {"reply": reply, "sources": ["CropPulse Navigation"]}

    if any(k in msg_lower for k in ["recommend", "what to grow", "which crop", "crop suggestion", "soil type", "climate"]):
        reply = (
            "To find the ideal crop for your specific soil and climate conditions, check out our "
            "**[Crop Recommendation](/crop-recommendation)** tool. Input your N-P-K, temperature, humidity, pH, and rainfall to receive ML-powered crop suggestions."
        )
        return {"reply": reply, "sources": ["CropPulse Navigation"]}

    if any(k in msg_lower for k in ["yield", "production", "harvest", "tonnes", "hectare", "how much"]):
        reply = (
            "To forecast your harvest output across 124 crops and multi-region seasonal data, use the "
            "**[Yield Prediction](/yield-prediction)** module. Enter your crop, region, season, and acreage for instant yield analytics."
        )
        return {"reply": reply, "sources": ["CropPulse Navigation"]}

    if any(k in msg_lower for k in ["fertilizer", "soil health", "npk", "nitrogen", "phosphorus", "potassium"]):
        reply = (
            "For tailored fertilizer dosages and soil health advisory based on your soil test parameters, visit the "
            "**[Soil Health & Fertilizers](/soil-health)** page."
        )
        return {"reply": reply, "sources": ["CropPulse Navigation"]}

    # 7. General Agriculture FAQ
    if any(k in msg_lower for k in ["drip", "irrigation", "water"]):
        reply = (
            "### 💧 Precision Irrigation Guidelines\n\n"
            "Drip irrigation delivers 30–50% water savings over flood irrigation and minimizes foliar diseases:\n"
            "- Irrigate early in the morning to allow quick surface drying.\n"
            "- Check drippers regularly for salt or algae clogging.\n"
            "- Tailor frequency to crop growth stage (flowering and fruit/grain filling are most sensitive to moisture deficit)."
        )
        return {"reply": reply, "sources": ["Water Management Handbook"]}

    if any(k in msg_lower for k in ["organic", "compost", "manure"]):
        reply = (
            "### 🍂 Organic Soil Conditioning Guidelines\n\n"
            "- **Compost / FYM**: Apply 8–10 tonnes/ha well-decomposed manure 2–3 weeks before sowing to improve water retention and soil biological life.\n"
            "- **Vermicompost**: Excellent rich source of humus, micronutrients, and beneficial microbes (apply 2–3 tonnes/ha).\n"
            "- **Bio-fertilizers**: Inoculate seed with *Rhizobium* (for legumes) or *Azotobacter* / *PSB* (for cereals) to unlock soil Phosphorus and fix Nitrogen."
        )
        return {"reply": reply, "sources": ["Organic Agriculture Manual"]}

    # 8. Friendly Fallback
    reply = (
        "Hello! I am your **CropPulse Agricultural Assistant**. I can help you with:\n\n"
        "- 🔬 **Plant Disease Diagnostics & Treatment Schedules** (upload or scan a leaf on the [Disease Detection](/disease-detection) page)\n"
        "- 🌾 **Crop Recommendation** based on soil and climate parameters\n"
        "- 📈 **124-Crop Yield Forecasting** for seasonal planning\n"
        "- 🧪 **Soil Health & Fertilizer Optimization**\n\n"
        "Feel free to ask any farming or crop management question!\n\n"
        "*(💡 Tip: To unlock open-ended conversational AI with Gemma, configure your free `OPENROUTER_API_KEY` in your environment or `.env` file.)*"
    )
    return {"reply": reply, "sources": ["CropPulse Guide"]}


# ── Main chat function ─────────────────────────────────────────────────────────
def chat(message: str, session_id: str, prediction_context: dict = None) -> dict:
    # Validate message length
    if len(message) > 500:
        return {
            "reply"  : "Your message is too long. Please keep it under 500 characters.",
            "sources": []
        }

    # Empty message check
    if not message.strip():
        return {
            "reply"  : "Please type a message.",
            "sources": []
        }

    client = get_client()

    # If no LLM API key configured, use built-in expert agricultural fallback
    if not client:
        return generate_expert_fallback(message, prediction_context)

    # Home page — skip RAG, just answer website navigation questions
    if not prediction_context:
        system_prompt = HOME_PROMPT
        full_prompt   = message
        sources       = []
    else:
        # Feature pages — retrieve context from vector DB
        context_text, sources   = retrieve_context(message, prediction_context)
        prediction_context_text = get_prediction_context_text(prediction_context)
        system_prompt           = get_system_prompt(prediction_context)

        full_prompt = CONTEXT_PROMPT_TEMPLATE.format(
            context            = context_text,
            prediction_context = prediction_context_text,
            question           = message
        )

    # Build conversation history
    if session_id not in _conversation_histories:
        _conversation_histories[session_id] = []

    history = _conversation_histories[session_id]

    # Build messages — merge system into first user message for Gemma compatibility
    messages = []
    for entry in history:
        messages.append({
            "role"   : entry["role"],
            "content": entry["content"]
        })

    merged_message = f"{system_prompt}\n\n{full_prompt}"
    messages.append({"role": "user", "content": merged_message})

    # Call Gemma via OpenRouter with retry logic
    max_retries = 2
    reply_text  = None

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model       = MODEL,
                messages    = messages,
                max_tokens  = 1024,
                temperature = 0.3,
            )
            reply_text = response.choices[0].message.content
            break  # success

        except Exception as e:
            error_str = str(e)
            print(f"OpenRouter API call attempt {attempt+1} failed: {error_str}")
            if "429" in error_str and attempt < max_retries - 1:
                time.sleep(3)
                continue
            # If all retries fail or other error, smoothly fall back to built-in expert
            return generate_expert_fallback(message, prediction_context)

    if not reply_text:
        return generate_expert_fallback(message, prediction_context)

    # Update conversation history
    history.append({"role": "user",      "content": message})
    history.append({"role": "assistant", "content": reply_text})

    # Keep only last MAX_HISTORY exchanges
    if len(history) > MAX_HISTORY * 2:
        _conversation_histories[session_id] = history[-(MAX_HISTORY * 2):]

    return {
        "reply"  : reply_text,
        "sources": sources
    }
