import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')
from chatbot.chat_service import chat

print("Testing Chatbot Fallback Engine...")

# Test 1: User's exact prompt from screenshot
r1 = chat(
    message='I just scanned a Corn (Maize) leaf showing signs of "Corn Gray Leaf Spot". Can you explain the treatment schedule and preventive management steps?',
    session_id='test1',
    prediction_context={'feature': 'disease_detection', 'crop': 'Corn (Maize)', 'disease': 'Corn Gray Leaf Spot'}
)
print("\n=== TEST 1 (DISEASE DETECTION CONTEXT) ===")
print("Sources:", r1.get("sources"))
print("Reply:\n", r1.get("reply"))

# Test 2: Disease inquiry without prediction context
r2 = chat(
    message='What are the treatment steps for Apple Scab?',
    session_id='test2'
)
print("\n=== TEST 2 (DISEASE MATCHING) ===")
print("Reply:\n", r2.get("reply"))

# Test 3: Crop recommendation context
r3 = chat(
    message='How do I manage this crop?',
    session_id='test3',
    prediction_context={'feature': 'crop_recommendation', 'crop': 'Rice'}
)
print("\n=== TEST 3 (CROP RECOMMENDATION) ===")
print("Reply:\n", r3.get("reply"))

# Test 4: Navigation inquiry
r4 = chat(
    message='Where can I predict crop yield?',
    session_id='test4'
)
print("\n=== TEST 4 (NAVIGATION) ===")
print("Reply:\n", r4.get("reply"))

print("\nAll tests completed successfully!")
