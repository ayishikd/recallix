"""
Deep diagnostic: trace exactly where retention memories get lost.
Tests each layer independently: SQLite -> C++ Vector -> MemoryRouter -> RecallEngine
"""
import requests
import time
import sqlite3

API_URL = "http://127.0.0.1:8000/memory"
CPP_URL = "http://localhost:8080"
API_KEY = "local_dev_key"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
DB_PATH = "backend/storage/sqlite_db/memory.db"
TEST_USER = "diag_user"

def step(name):
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")

def main():
    # ── STEP 0: Clear everything ──
    step("STEP 0: Clear all state")
    r = requests.post("http://127.0.0.1:8000/internal/clear", json={"user_id": TEST_USER}, headers=HEADERS)
    print(f"  Clear response: {r.status_code} {r.text[:100]}")

    # ── STEP 1: Store exactly 3 facts via API ──
    step("STEP 1: Store 3 facts via /memory/store")
    facts = [
        "The user's favorite color is midnight blue.",
        "The project deadline is December 12th.",
        "The user has a cat named Pixel."
    ]
    for i, fact in enumerate(facts):
        r = requests.post(f"{API_URL}/store", json={
            "content": fact, 
            "user_id": TEST_USER, 
            "skip_llm": True
        }, headers=HEADERS)
        print(f"  Stored fact {i}: status={r.status_code}")
    
    time.sleep(0.5)  # Let everything settle

    # ── STEP 2: Check SQLite directly ──
    step("STEP 2: Check SQLite for diag_user")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, agent_id, memory_type, content, timestamp FROM episodic_events WHERE user_id = ? ORDER BY id DESC LIMIT 10", (TEST_USER,))
    rows = cursor.fetchall()
    print(f"  Found {len(rows)} rows for user '{TEST_USER}'")
    for r in rows:
        print(f"    ID={r[0]} user={r[1]} agent={r[2]} type={r[3]} content='{r[4][:40]}...' ts={r[5]}")
    conn.close()

    # ── STEP 3: Check C++ vector engine directly ──
    step("STEP 3: Query C++ engine directly for 'favorite color'")
    from sentence_transformers import SentenceTransformer
    import numpy as np
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    query_text = "favorite color"
    vec = model.encode(query_text).astype(np.float32)
    vec = (vec / np.linalg.norm(vec)).tolist()
    
    r = requests.post(f"{CPP_URL}/search_vector", json={"query": vec, "top_k": 5})
    print(f"  C++ response status: {r.status_code}")
    if r.status_code == 200:
        results = r.json().get("results", [])
        print(f"  C++ returned {len(results)} results:")
        for res in results:
            print(f"    id='{res['id']}' score={res['score']:.4f}")
            # Check if this ID belongs to our test user
            parts = res['id'].split("::")
            if len(parts) >= 4:
                print(f"      -> user={parts[0]} agent={parts[1]} type={parts[2]} ts={parts[3]} sqlite_id={parts[4] if len(parts)>4 else 'N/A'}")

    # ── STEP 4: Query via the full recall API ──
    step("STEP 4: Full /memory/recall for 'favorite color'")
    r = requests.post(f"{API_URL}/recall", json={
        "query": "favorite color",
        "user_id": TEST_USER
    }, headers=HEADERS)
    print(f"  Recall response status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()["data"]
        mems = data.get("memories", [])
        print(f"  Memories returned: {len(mems)}")
        for m in mems[:5]:
            if isinstance(m, dict):
                print(f"    content='{m.get('content', 'N/A')[:50]}...' ")
            else:
                print(f"    raw: {str(m)[:80]}")
        print(f"  Intent: {data.get('intent')}")
        print(f"  Latency: {data.get('latency_ms', 'N/A')}ms")

    # ── STEP 5: Check what the retention benchmark query looks like ──
    step("STEP 5: Test with exact retention benchmark query")
    fact = "The user's favorite color is midnight blue."
    query = fact.split("is")[0] if "is" in fact else fact[:20]
    print(f"  Query text: '{query}'")
    r = requests.post(f"{API_URL}/recall", json={
        "query": query,
        "user_id": TEST_USER
    }, headers=HEADERS)
    if r.status_code == 200:
        data = r.json()["data"]
        mems = data.get("memories", [])
        print(f"  Memories returned: {len(mems)}")
        for m in mems[:5]:
            if isinstance(m, dict):
                content = m.get('content', 'N/A')
                print(f"    content='{content[:60]}...'")
                # Check if the original fact is in here
                if fact[:15].lower() in content.lower():
                    print(f"    ✅ MATCH FOUND")
                else:
                    print(f"    ❌ No match (looking for '{fact[:15]}')")
            else:
                print(f"    raw: {str(m)[:80]}")

if __name__ == "__main__":
    main()
