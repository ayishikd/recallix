import time
import requests
import json

BRAIN_URL = "http://localhost:8000"

def test_memory_flow():
    user_id = "user_123"
    messages = [
        "Hello, my name is Alice.",
        "I like hiking and coffee.",
        "Remember that I am allergic to peanuts.", # High importance
        "What do you know about me?"
    ]

    for msg in messages[:-1]:
        print(f"Storing: {msg}")
        requests.post(f"{BRAIN_URL}/memory/store", json={"user_id": user_id, "message": msg})
        time.sleep(1)

    print("\nRetrieving context (Cognitive Recall Pipeline):")
    res = requests.get(f"{BRAIN_URL}/memory/retrieve", params={"user_id": user_id, "query": "peanuts"})
    print(f"Response status: {res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print(f"Prediction (Topic): {data.get('prediction', {}).get('topic')}")
        print(f"Sensory: {len(data.get('sensory', []))} items")
        print(f"Episodic: {len(data.get('episodic', []))} items")
        print(f"Long Term: {len(data.get('long_term', []))}")
        print(f"Reflective: {len(data.get('reflective', []))}")
        for r in data.get("reflective", []):
             print(f" - Insight: {r['summary']} (Conf: {r['confidence']})")
    else:
        print(f"Error: {res.text}")

if __name__ == "__main__":
    # Note: This requires both C++ infra and Python brain to be running
    print("Disclaimer: This script assumes backend services are running.")
    test_memory_flow()
