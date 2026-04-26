import requests
import json
import time

API_URL = "http://127.0.0.1:8000/memory"
API_KEY = "local_dev_key"

HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_intent_recall(query, expected_intent):
    payload = {"query": query}
    
    print(f"\n[TEST] Query: {query}")
    start = time.time()
    response = requests.post(f"{API_URL}/recall", json=payload, headers=HEADERS)
    elapsed = (time.time() - start) * 1000
    
    if response.status_code == 200:
        data = response.json()["data"]
        detected_intent = data.get("intent")
        memories = data.get("memories", [])
        plan = data.get("retrieval_plan", {})
        
        print(f"Detected Intent: {detected_intent} (Confidence: {data.get('confidence'):.2f})")
        print(f"Inferred Topic: {data.get('context_inference', {}).get('topic')}")
        print(f"Retrieval Plan (Memory Types): {plan.get('memory_types')}")
        print(f"Memory Count: {len(memories)}")
        print(f"Pipeline Latency: {data.get('latency_ms'):.1f}ms (Total API: {elapsed:.1f}ms)")
        
        if detected_intent == expected_intent:
            print("✅ Intent Match!")
        else:
            print(f"❌ Intent Mismatch! Expected {expected_intent}")
            
        return data
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    # 1. Learning Intent
    test_intent_recall("How does recursion work in Python?", "learning")
    
    # 2. Preference Intent
    test_intent_recall("I prefer spicy food and like sushi.", "preference_update")
    
    # 3. Task Intent
    test_intent_recall("Can we plan the project execution?", "task_execution")
    
    # 4. Research Intent
    test_intent_recall("Compare scikit-learn and spatcy for topic clustering.", "research")
    
    # 5. Generic Conversation
    test_intent_recall("Hey, how are you doing today?", "conversation")
