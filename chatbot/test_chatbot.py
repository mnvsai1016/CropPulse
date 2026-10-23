from chatbot.chat_service import chat

print("=== Agri-Guide Chatbot Test ===\n")

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