import sqlite3
import time
import os
import json
import requests

BRAIN_URL = "http://localhost:8000"
TIMELINE_DB = "backend/storage/timeline_store/timeline.db"
REFLECTIONS_DB = "backend/storage/sqlite_db/reflections.db"
META_DB = "backend/storage/sqlite_db/meta_memory.db"
REGISTRY_PATH = "backend/storage/schema_registry.json"
POLICY_PATH = "backend/storage/memory_policies.json"

def seed_data(user_id):
    print("Seeding recurring patterns into Timeline and Reflections...")
    
    # 1. Seed Timeline with "recursion" pattern
    conn = sqlite3.connect(TIMELINE_DB)
    cursor = conn.cursor()
    events = [
        "User is asking about recursive functions in C++.",
        "User struggling with base case in recursion.",
        "User repeatedly asking how to optimize recursion.",
        "User mentioned wanting to master recursive algorithms."
    ]
    for event in events:
        cursor.execute("INSERT INTO events (user_id, event_content, timestamp) VALUES (?, ?, ?)", 
                       (user_id, event, time.time()))
    conn.commit()
    conn.close()

    # 2. Seed Reflections with similar theme
    conn = sqlite3.connect(REFLECTIONS_DB)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reflections (user_id, summary, source_memories, confidence, timestamp) VALUES (?, ?, ?, ?, ?)",
                   (user_id, "User has recurring difficulty with recursion.", "1,2,3", 0.9, time.time()))
    conn.commit()
    conn.close()

def test_meta_evolution():
    user_id = "user_meta_test"
    
    # Clean up old data if any
    if os.path.exists(META_DB): os.remove(META_DB)
    if os.path.exists(REGISTRY_PATH): os.remove(REGISTRY_PATH)
    if os.path.exists(POLICY_PATH): os.remove(POLICY_PATH)

    seed_data(user_id)
    
    print("\n--- Phase 1: Running Meta-Memory Analysis ---")
    from backend.brain.memory.manager import MemoryManager
    from backend.brain.workers.meta_memory_worker import MetaMemoryWorker
    
    manager = MemoryManager()
    worker = MetaMemoryWorker(manager)
    worker.run_analysis(user_id)

    # 3. Verify Schema Evolution
    print("\n--- Phase 2: Verifying Schema Evolution ---")
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, 'r') as f:
            registry = json.load(f)
            schemas = [s["name"] for s in registry.get("schemas", [])]
            print(f"Evolved Schemas: {schemas}")
            if "recursion_interest" in schemas:
                print("SUCCESS: schema 'recursion_interest' evolved!")
            else:
                print("FAILURE: schema not evolved.")
    else:
        print("FAILURE: registry file not found.")

    # 4. Verify Policy Optimization
    print("\n--- Phase 3: Verifying Policy Optimization ---")
    if os.path.exists(POLICY_PATH):
        with open(POLICY_PATH, 'r') as f:
            policies = json.load(f)
            weights = policies.get("importance_weights", {})
            print(f"Optimized Weights: {weights}")
            if weights.get("user_goals", 1.2) > 1.2:
                print("SUCCESS: importance weights optimized!")
            else:
                print("FAILURE: weights not optimized.")
    else:
        print("FAILURE: policy file not found.")

    # 5. Verify Meta-Insights Storage
    print("\n--- Phase 4: Verifying Meta-Insights Storage ---")
    conn = sqlite3.connect(META_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT meta_type, insight_text FROM meta_insights")
    insights = cursor.fetchall()
    print("Logged meta-insights:")
    for type, text in insights:
        print(f"- [{type}] {text}")
    conn.close()
    if len(insights) >= 2:
        print("SUCCESS: insights logged correctly!")
    else:
        print("FAILURE: insufficient insights logged.")

if __name__ == "__main__":
    test_meta_evolution()
