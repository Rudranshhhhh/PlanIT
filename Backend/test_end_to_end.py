import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(response.json())
        else:
            print(f"❌ Health check failed: {response.text}")
    except Exception as e:
        print(f"❌ Connection error: {e}")

def test_chat_turn(message, reset=False):
    print(f"\nSending message: '{message}'")
    if reset:
        requests.post(f"{BASE_URL}/reset")
        print("🔄 Conversation reset.")

    payload = {"message": message}
    start_time = time.time()
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=60)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response", "")
            print(f"✅ Response received in {elapsed:.2f}s:")
            print("-" * 40)
            print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
            print("-" * 40)
            
            # Verification checks
            if "trip" in message.lower() or "plan" in message.lower():
                if any(x in response_text.lower() for x in ["itinerary", "day 1", "budget", "hotel"]):
                    print("✅ Response looks like a valid plan.")
                else:
                    print("⚠️ Response might lack specific planning details.")
            
            if "INR" in response_text or "₹" in response_text:
                print("✅ Currency handled correctly (INR detected).")
            
        else:
            print(f"❌ Chat request failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error during chat request: {e}")

if __name__ == "__main__":
    print("🚀 Starting End-to-End Chatbot Test")
    test_health()
    
    # Test 1: Simple greeting
    test_chat_turn("Hello, who are you?", reset=True)
    
    # Test 2: Complex planning task
    test_chat_turn("Plan a 2-day trip to Jaipur for me. I have a budget of 15000 INR.")
