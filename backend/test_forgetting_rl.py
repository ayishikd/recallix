import requests
import time
import sqlite3
import os
import json

BRAIN_URL = "http://localhost:8000"
DB_PATH = "backend/storage/sqlite_db/memory.db"
ARCHIVE_PATH = "backend/storage/archive_store/archived_memories.db"

def wait_for_server():
    print("Waiting for server...")
    for _ in range(30):
        try:
            res = requests.get(f"{BRAIN_URL}/docs")
            if res.status_code == 200:
                print("Server is ready!")
                return True
        except:
            pass
        time.sleep(2)
    return False

def test_forgetting_rl():
    user_id = "user_rl_test"
    print(f"Starting test for user: {user_id}")
    
    # 1. Store Diverse Memories
    memories = [
        ("I am learning about quantum physics.", 9),  # High importance
        ("The sky is blue today.", 2),               # Low importance
        ("Remind me to buy milk.", 5)                # Medium importance
    ]
    
    print("\n--- Phase 1: Storing Memories ---")
    for content, imp in memories:
        res = requests.post(f"{BRAIN_URL}/memory/store", json={
            "user_id": user_id,
            "message": f"IMPORTANT: {content}" if imp > 8 else content
        })
        print(f"Stored: {content} | Status: {res.status_code}")

    time.sleep(2)

    # 2. Trigger Reinforcement via Retrieval
    print("\n--- Phase 2: Triggering Reinforcement ---")
    query = "quantum physics learning"
    for i in range(3):
        res = requests.get(f"{BRAIN_URL}/memory/retrieve", params={"user_id": user_id, "query": query})
        print(f"Retrieval {i+1} for '{query}' | Status: {res.status_code}")
        time.sleep(1)

    # Check reinforcement in DB
    conn = sqlite3.connect(DB_PATH, timeout=60)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("SELECT content, reinforcement_score, retrieval_count FROM episodic_events WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    print("\nCurrent Reinforcement Scores:")
    for row in rows:
        print(f"- {row[0][:30]}... | Score: {row[1]:.2f} | Count: {row[2]}")
    conn.close()

    # 3. Simulate Aging (Set timestamps to 100 days ago for low/medium value)
    print("\n--- Phase 3: Simulating Aging ---")
    old_ts = time.time() - (100 * 24 * 3600)
    
    # Retry logic for DB update
    for _ in range(5):
        try:
            conn = sqlite3.connect(DB_PATH, timeout=60)
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            # Age "The sky is blue" (low importance, low reinforcement)
            cursor.execute("UPDATE episodic_events SET timestamp = ? WHERE content LIKE '%sky is blue%'", (old_ts,))
            # Age "Remind me to buy milk" (medium importance, low reinforcement)
            cursor.execute("UPDATE episodic_events SET timestamp = ? WHERE content LIKE '%buy milk%'", (old_ts,))
            conn.commit()
            conn.close()
            print("Aged specific memories by 100 days.")
            break
        except sqlite3.OperationalError as e:
            print(f"DB locked, retrying... {e}")
            time.sleep(2)

    # 4. Trigger Forgetting Worker
    print("\n--- Phase 4: Triggering Forgetting Worker ---")
    # Instead of waiting for background thread, we'll manually invoke the method via a temp script or endpoint if added
    # For now, we'll use a direct call by importing the worker logic if possible, or just wait if we set a short interval.
    # Since we can't easily import from the script here without path issues, we'll use a one-off script.
    
    worker_trigger = """
import sys
import os
sys.path.append(os.getcwd())
from backend.brain.memory.manager import MemoryManager
from backend.brain.workers.forgetting_worker import ForgettingWorker
manager = MemoryManager()
worker = ForgettingWorker(manager)
print("Running worker.run_cleanup()...")
worker.run_cleanup()
print("Cleanup done.")
"""
    with open("/tmp/trigger_forgetting.py", "w") as f:
        f.write(worker_trigger)
    
    os.system("./venv/bin/python3 /tmp/trigger_forgetting.py")

    # 5. Final Verification
    print("\n--- Phase 5: Final Verification ---")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM episodic_events WHERE user_id = ?", (user_id,))
    remaining = [r[0] for r in cursor.fetchall()]
    conn.close()
    
    print("Remaining Memories in Primary Store:")
    for r in remaining:
        print(f"- {r}")

    # Check Archive
    if os.path.exists(ARCHIVE_PATH):
        conn = sqlite3.connect(ARCHIVE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM archived_memories")
        archived = [r[0] for r in cursor.fetchall()]
        conn.close()
        print("\nArchived Memories:")
        for a in archived:
            print(f"- {a}")
    else:
        print("\nArchive DB not created yet.")

if __name__ == "__main__":
    if wait_for_server():
        test_forgetting_rl()
