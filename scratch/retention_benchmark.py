import requests
import json
import time
import numpy as np
import matplotlib.pyplot as plt
import os

API_URL = "http://127.0.0.1:8000/memory"
API_KEY = "local_dev_key"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

VANILLA_CONTEXT_WINDOW = 20 # Turns a standard LLM remembers

_store_count = 0

def store_fact(fact, timestamp=None):
    global _store_count
    payload = {"content": fact}
    if timestamp:
        payload["timestamp"] = timestamp
    
    t0 = time.time()
    res = requests.post(f"{API_URL}/store", json=payload, headers=HEADERS)
    dt = (time.time() - t0) * 1000
    
    _store_count += 1
    if _store_count % 10 == 0:
        print(f"   Processed {_store_count} turns... (Last turn: {dt:.1f}ms)", flush=True)
    
    return res.status_code == 200

def query_fact(query):
    payload = {"query": query}
    res = requests.post(f"{API_URL}/recall", json=payload, headers=HEADERS)
    if res.status_code == 200:
        return res.json()["data"]["memories"]
    return []

def run_retention_benchmark():
    print("🚀 Starting Long-Term Retention Benchmark...")
    
    # 1. Setup Golden Facts at different depths
    golden_facts = [
        (1, "The user's favorite book is 'The Catcher in the Rye'.", "What is the user's favorite book?"),
        (50, "The secret project code is 'OMEGA-2026'.", "What is the secret project code?"),
        (100, "The anniversary date is June 15th.", "When is the anniversary date?"),
        (250, "The cat's name is 'Nebula'.", "What is the cat's name?"),
        (400, "The server password is 'r3c4ll-m3-n0w'.", "What is the server password?"),
        (499, "The final meeting location is the moon.", "Where is the final meeting location?")
    ]
    
    total_turns = 500
    retention_recallix = []
    retention_vanilla = []
    
    print(f"📥 Simulating {total_turns} turns of conversation...")
    
    for turn in range(1, total_turns + 1):
        fact_to_store = None
        for depth, content, _ in golden_facts:
            if turn == depth:
                fact_to_store = content
                break
        
        if fact_to_store:
            store_fact(fact_to_store)
        else:
            store_fact(f"This is turn {turn} of a very long conversation about nothing important.")

    # 2. Testing Retention
    print(f"\n🔍 Testing memory retention across depths...")
    
    for depth, content, query in golden_facts:
        vanilla_retains = (total_turns - depth) < VANILLA_CONTEXT_WINDOW
        retention_vanilla.append(100 if vanilla_retains else 0)
        
        print(f"   Querying fact from turn {depth}: '{query}'")
        memories = query_fact(query)
        
        found = False
        for m in memories:
            m_content = m if isinstance(m, str) else m.get("content", "")
            keywords = content.split()[-2:]
            if all(k.lower().strip(".,'\"") in m_content.lower() for k in keywords):
                found = True
                break
        
        retention_recallix.append(100 if found else 0)
        status = "✅" if found else "❌"
        print(f"      Recallix: {status} | Vanilla: {'✅' if vanilla_retains else '❌'}")

    # 3. Plotting
    turns_axis = [depth for depth, _, _ in golden_facts]
    
    plt.figure(figsize=(10, 6))
    plt.step(turns_axis, retention_vanilla, label="Vanilla LLM (20-turn window)", where='post', color='red', linestyle='--')
    plt.scatter(turns_axis, retention_recallix, label="MemoryOS (Recallix)", color='green', s=100)
    plt.plot(turns_axis, retention_recallix, color='green', linewidth=2)
    
    plt.xlabel('Turn Number (Age of Memory)')
    plt.ylabel('Retention Rate (%)')
    plt.title('Long-Term Retention: MemoryOS vs Vanilla LLM')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(-10, 110)
    plt.xlim(0, 510)

    plot_path = "backend/docs/retention_benchmark.png"
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)
    plt.savefig(plot_path)
    print(f"\n📈 Retention plot saved to {plot_path}")

if __name__ == "__main__":
    run_retention_benchmark()
