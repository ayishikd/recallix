import requests
import time
import random

API_URL = "http://127.0.0.1:8000/memory"
HEADERS = {"X-API-Key": "local_dev_key", "Content-Type": "application/json"}
USER = "gauntlet_runner"

def clear():
    requests.post("http://127.0.0.1:8000/internal/clear", json={"user_id": USER}, headers=HEADERS)

def store(content, metadata=None):
    requests.post(f"{API_URL}/store", json={"user_id": USER, "content": content, "metadata": metadata, "skip_llm": True}, headers=HEADERS)

def recall(query):
    res = requests.post(f"{API_URL}/recall", json={"query": query, "user_id": USER, "top_k": 5}, headers=HEADERS)
    return res.json()["data"]["memories"]

def run_gauntlet():
    print("\n🔥 Starting Recallix Gauntlet v1 (Adversarial Stress Test) 🔥")
    clear()
    
    # --- TEST 1: Temporal Contradiction ---
    print("\n[Test 1] Temporal Contradiction (Truth Evolution)...")
    store("Galaxy X-55 primary emission is Synchrotron Radiation.")
    time.sleep(1.1) # Ensure timestamp difference
    store("ALERT: Galaxy X-55 has shifted states. Primary emission is now Inverse Compton Scattering.")
    
    mems = recall("What is the CURRENT primary cause of emission in Galaxy X-55?")
    if mems and "Inverse Compton" in mems[0]["content"]:
        print("   ✅ PASS: Prioritized Recency/State-Shift.")
    else:
        print(f"   ❌ FAIL: Stuck on stale truth. Top result: {mems[0]['content'] if mems else 'None'}")

    # --- TEST 2: Noisy Identity & Slang ---
    print("\n[Test 2] Noisy Identity (Out-of-Regex Slang)...")
    store("The project known as 'Crimson Sky' is based in the Martian Highlands.")
    
    # Query with slang/typo/vague reference
    mems = recall("Where is that red-heaven mission located?")
    if mems and "Crimson Sky" in mems[0]["content"]:
        print("   ✅ PASS: Semantic recovery worked for slang.")
    else:
        print(f"   ❌ FAIL: Identity-locking vaporized the semantic match. Top score: {mems[0]['unified_score'] if mems else '0.0'}")

    # --- TEST 3: One-Token Adversarial Distractors ---
    print("\n[Test 3] One-Token Adversarial Distractors...")
    store("Galaxy X-101 Primary Emission: Blackbody Radiation.") # Correct
    store("Galaxy X-102 Primary Emission: Blackbody Radiation.") # Distractor 1 (Similar Identity)
    store("Galaxy X-101 Secondary Signature: Blackbody Radiation.") # Distractor 2 (Similar Relation)
    
    mems = recall("Explain the primary emission cause for Galaxy X-101.")
    if mems and "Galaxy X-101 Primary Emission" in mems[0]["content"]:
        print("   ✅ PASS: Precision-locked to correct Entity+Relation.")
    else:
        print(f"   ❌ FAIL: Collision! Top result: {mems[0]['content'] if mems else 'None'}")

    # --- TEST 4: The Ghost Query (Hallucination Check) ---
    print("\n[Test 4] The Ghost Query (False Positive Check)...")
    mems = recall("What is the primary cause of emission in the Andromeda-9 Nebula?")
    top_score = mems[0]["unified_score"] if mems else 0.0
    if top_score < 0.2:
        print(f"   ✅ PASS: Correctly reported low confidence ({top_score:.2f}).")
    else:
        print(f"   ❌ FAIL: Hallucinated a match! Score: {top_score:.2f}, Content: {mems[0]['content']}")

if __name__ == "__main__":
    run_gauntlet()
