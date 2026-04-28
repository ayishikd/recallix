import requests
import time

API_URL = "http://127.0.0.1:8000/memory"
HEADERS = {"X-API-Key": "local_dev_key", "Content-Type": "application/json"}
USER = "gauntlet_v3_runner"

def clear():
    requests.post("http://127.0.0.1:8000/internal/clear", json={"user_id": USER}, headers=HEADERS)

def store(content, metadata=None):
    requests.post(f"{API_URL}/store", json={"user_id": USER, "content": content, "metadata": metadata, "skip_llm": True}, headers=HEADERS)

def recall(query):
    res = requests.post(f"{API_URL}/recall", json={"query": query, "user_id": USER, "top_k": 5}, headers=HEADERS)
    return res.json()["data"]

def run_gauntlet_v3():
    print("\n💀 Starting Recallix Gauntlet v3 (The Cognitive Wall) 💀")
    clear()
    
    # --- TEST 1: Multi-Hop Reasoning ---
    print("\n[Test 1] Multi-Hop Reasoning (Knowledge Chaining)...")
    clear()
    store("Galaxy X-1 contains the Pulsar P-42.")
    store("Pulsar P-42 emits high-energy Gamma Rays.")
    
    res = recall("What kind of radiation does Galaxy X-1 effectively emit via its contents?")
    mems = res["memories"]
    if mems and any("Gamma Rays" in m["content"] for m in mems):
        print("   ✅ PASS: Chained X-1 -> P-42 -> Gamma Rays.")
    else:
        print(f"   ❌ FAIL: Could not bridge the facts. Top result: {mems[0]['content'] if mems else 'None'}")

    # --- TEST 2: Contextual Qualifiers (State-Dependent Truth) ---
    print("\n[Test 2] Contextual Qualifiers (State-Dependent Truth)...")
    clear()
    store("Galaxy X-55 emits X-rays during its Active Phase.")
    store("Galaxy X-55 emits Radio waves during its Quiescent Phase.")
    
    res = recall("What is X-55's primary emission when it is dormant?")
    mems = res["memories"]
    if mems and "Radio waves" in mems[0]["content"]:
        print("   ✅ PASS: Respected 'dormant' (Quiescent) context.")
    else:
        print(f"   ❌ FAIL: Hallucinated or returned wrong phase. Top result: {mems[0]['content'] if mems else 'None'}")

    # --- TEST 3: Entity Alias Resolution ---
    print("\n[Test 3] Entity Alias Resolution...")
    clear()
    store("Galaxy X-77 is colloquially known as 'The Dragon's Breath'.")
    store("The primary energy source of X-77 is a Supermassive Black Hole.")
    
    res = recall("What powers 'The Dragon's Breath'?")
    mems = res["memories"]
    if mems and "Black Hole" in mems[0]["content"]:
        print("   ✅ PASS: Resolved 'The Dragon's Breath' to X-77.")
    else:
        print(f"   ❌ FAIL: Failed to link alias. Top result: {mems[0]['content'] if mems else 'None'}")

    # --- TEST 4: Contradiction Detection ---
    print("\n[Test 4] Contradiction Detection (Truth Conflicts)...")
    clear()
    store("Mission Log: The reactor core of the Starship Daedalus is Stable.")
    store("ALERT: Sensory scan indicates Starship Daedalus reactor core is CRITICAL.")
    
    res = recall("What is the safety status of the Daedalus reactor?")
    mems = res["memories"]
    # In a perfect system, this should flag a conflict or return the LATEST (critical)
    if mems and "CRITICAL" in mems[0]["content"]:
        print("   ✅ PASS: Prioritized the urgent/latest update.")
    else:
        print(f"   ❌ FAIL: Stuck on stale 'Stable' fact. Top result: {mems[0]['content'] if mems else 'None'}")

if __name__ == "__main__":
    run_gauntlet_v3()
