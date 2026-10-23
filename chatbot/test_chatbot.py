import os
import sys

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chatbot.chat_service import chat

print("=== CropPulse Assistant Test ===\n")

result = chat(
    message="How do I improve soil fertility organically?",
    session_id="test-session-1"
)
print("Q: How do I improve soil fertility organically?")
print(f"A: {result['reply']}")
print(f"Sources: {result['sources']}\n")

result2 = chat(
    message="What are the best practices for growing this crop?",
    session_id="test-session-2",
    prediction_context={
        "feature": "crop_recommendation",
        "crop": "Rice"
    }
)
print("Q: What are the best practices for growing this crop? [Context: Rice]")
print(f"A: {result2['reply']}")
print(f"Sources: {result2['sources']}\n")

result3 = chat(
    message="How should I apply this fertilizer?",
    session_id="test-session-3",
    prediction_context={
        "feature": "soil_health",
        "fertilizer": "Urea"
    }
)
print("Q: How should I apply this fertilizer? [Context: Urea]")
print(f"A: {result3['reply']}")
print(f"Sources: {result3['sources']}\n")

result4 = chat(
    message='I just scanned a Corn (Maize) leaf showing signs of "Corn Gray Leaf Spot". Can you explain the treatment schedule and preventive management steps?',
    session_id="test-session-4",
    prediction_context={
        "feature": "disease_detection",
        "crop": "Corn (Maize)",
        "disease": "Corn Gray Leaf Spot"
    }
)
print("Q: Corn Gray Leaf Spot diagnosis [Context: disease_detection]")
print(f"A: {result4['reply']}")
print(f"Sources: {result4['sources']}\n")
