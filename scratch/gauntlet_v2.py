import requests
import time
import random

API_URL = "http://127.0.0.1:8000/memory"
HEADERS = {"X-API-Key": "local_dev_key", "Content-Type": "application/json"}
USER = "gauntlet_v2_runner"

def clear():
    requests.post("http://127.0.0.1:8000/internal/clear", json={"user_id": USER}, headers=HEADERS)

def store(content, metadata=None):
    requests.post(f"{API_URL}/store", json={"user_id": USER, "content": content, "metadata": metadata, "skip_llm": True}, headers=HEADERS)

def recall(query):
    res = requests.post(f"{API_URL}/recall", json={"query": query, "user_id": USER, "top_k": 5}, headers=HEADERS)
    return res.json()["data"]

def run_gauntlet_v2():
    print("\n🔥 Starting Recallix Gauntlet v2 (The Open World Stress Test) 🔥")
    clear()
    
    # --- TEST 1: Schema Violation (Entity Typos) ---
    print("\n[Test 1] Schema Violation (Entity Typos)...")
    store("Galaxy X-63 Primary Emission: Synchrotron Radiation.")
    
    # Query with slightly different format
    res = recall("What is the primary cause of emission in galaxy x63?")
    mems = res["memories"]
    if mems and "Synchrotron" in mems[0]["content"]:
        print("   ✅ PASS: Resolved 'galaxy x63' to 'Galaxy X-63'.")
    else:
        print(f"   ❌ FAIL: Typo broke the lock. Top result: {mems[0]['content'] if mems else 'None'}")

    # --- TEST 2: Linguistic Drift (Semantic Relations) ---
    print("\n[Test 2] Linguistic Drift (Semantic Relations)...")
    store("Galaxy X-99 Primary Emission: Thermal Bremsstrahlung.")
    
    # Query with completely different vocabulary
    res = recall("How does the X-99 system generate its glow?")
    mems = res["memories"]
    if mems and "Thermal Bremsstrahlung" in mems[0]["content"]:
        print("   ✅ PASS: Semantic recovery bridged the relation gap.")
    else:
        print(f"   ❌ FAIL: Relation lock is too rigid. Top result: {mems[0]['content'] if mems else 'None'}")

    # --- TEST 3: Cross-Domain Collision ---
    print("\n[Test 3] Cross-Domain Collision (Identity Confusion)...")
    store("Galaxy X-100 Primary Emission: Blackbody Radiation.") # Astrophysics
    store("Patient X-100 Status: Critical condition in ICU.")     # Medical
    
    # Query for the galaxy
    res = recall("What is the emission type of the X-100 celestial object?")
    mems = res["memories"]
    if mems and "Galaxy X-100" in mems[0]["content"]:
        print("   ✅ PASS: Correctly differentiated Galaxy from Patient.")
    else:
        print(f"   ❌ FAIL: Collided! Top result: {mems[0]['content'] if mems else 'None'}")

    # --- TEST 4: Schema Violation (Ambiguous Facts) ---
    print("\n[Test 4] Schema Violation (Ambiguous Facts)...")
    store("The X-77 project is currently over budget by 40%.") # No 'Primary' label
    
    res = recall("Status of X-77?")
    mems = res["memories"]
    if mems and "over budget" in mems[0]["content"]:
        print("   ✅ PASS: Retrieved ambiguous fact without schema tags.")
    else:
        print(f"   ❌ FAIL: Squelched by strict schema ranking. Top score: {mems[0]['unified_score'] if mems else '0.0'}")

if __name__ == "__main__":
    run_gauntlet_v2()
