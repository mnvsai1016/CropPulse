import os
import time
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
    if not api_key:
        return None
    return OpenAI(
        base_url = "https://openrouter.ai/api/v1",
        api_key  = api_key
    )

MODEL       = "google/gemma-3-4b-it:free"
MAX_HISTORY = 5

_conversation_histories = {}


# ── Pick system prompt based on page ──────────────────────────────────────────
def get_system_prompt(prediction_context: dict) -> str:
    if not prediction_context:
        return HOME_PROMPT  # home page — no context = website guide mode

    feature = prediction_context.get("feature", "")

    if feature in ["crop_recommendation", "yield_prediction", "soil_health"]:
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

    return "None"


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

    client = get_client()
    if not client:
        return {
            "reply": "Chatbot is not configured yet. Please set your OPENROUTER_API_KEY in your environment or .env file.",
            "sources": []
        }

    # Call Gemma via OpenRouter with retry logic
    max_retries = 3
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
            if "429" in error_str and attempt < max_retries - 1:
                print(f"Rate limited, retrying in 10 seconds... (attempt {attempt + 1})")
                time.sleep(10)
                continue
            elif attempt == max_retries - 1:
                return {
                    "reply"  : "I am currently busy due to high demand. Please try again in a moment.",
                    "sources": []
                }
            else:
                return {
                    "reply"  : "Sorry, I encountered an error. Please try again.",
                    "sources": []
                }

    # Update conversation history
    history.append({"role": "user",      "content": merged_message})
    history.append({"role": "assistant", "content": reply_text})

    # Keep only last MAX_HISTORY exchanges
    if len(history) > MAX_HISTORY * 2:
        _conversation_histories[session_id] = history[-(MAX_HISTORY * 2):]

    return {
        "reply"  : reply_text,
        "sources": sources
    }