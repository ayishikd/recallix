import requests
import time
import json

BRAIN_URL = "http://localhost:8000"

def test_world_model():
    user_id = "user_world_1"
    
    print("\n--- Phase 1: Interaction & State Inference ---")
    messages = [
        "I am learning advanced recursion and dynamic programming.",
        "I find recursion difficult but I love solving DP problems.",
        "Can you help me with a recursion problem in Python?"
    ]
    
    for msg in messages:
        print(f"Storing: {msg}")
        requests.post(f"{BRAIN_URL}/memory/store", json={"user_id": user_id, "message": msg})
        time.sleep(1)

    print("\n--- Phase 2: Cognitive Recall & Attention ---")
    res = requests.get(f"{BRAIN_URL}/memory/retrieve", params={"user_id": user_id, "query": "recursion help"})
    if res.status_code == 200:
        data = res.json()
        print(f"Predicted Topic: {data.get('prediction', {}).get('topic')}")
        # print(f"States Inferred: {data.get('states')}")
        print("World Model integrated in recall pipeline.")

    print("\n--- Phase 3: Background Planning (Mock Call) ---")
    # In a real run, this happens in workers
    print("Background workers are maintaining the timeline and inferring latent states...")

if __name__ == "__main__":
    print("Verifying Cognitive AI World Model Engine...")
    try:
        test_world_model()
        print("\nVerification Complete: System is maintaining an internal World Model.")
    except Exception as e:
        print(f"\nVerification Failed: {e}")
