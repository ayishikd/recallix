import sqlite3
import requests

def inspect_system():
    db_path = "backend/storage/sqlite_db/memory.db"
    print(f"📊 Inspecting SQLite Database: {db_path}")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM episodic_events")
        count = cursor.fetchone()[0]
        print(f"   Total Memories: {count}")
        
        cursor.execute("SELECT id, user_id, agent_id, content, timestamp FROM episodic_events ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        print("\n   Latest 5 Memories:")
        for r in rows:
            print(f"   ID: {r[0]} | User: {r[1]} | Agent: {r[2]} | Content: {r[3][:30]}...")
            
        conn.close()
    except Exception as e:
        print(f"   ❌ DB Error: {e}")

    print("\n🔍 Checking C++ Vector Engine directly...")
    try:
        # Get a sample embedding for "color"
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        vec = model.encode("color").tolist()
        
        res = requests.post("http://localhost:8080/search_vector", json={"query": vec, "top_k": 5})
        if res.status_code == 200:
            results = res.json().get("results", [])
            print(f"   C++ Results found: {len(results)}")
            for r in results:
                print(f"   ID in C++: {r['id']} | Score: {r['score']:.4f}")
        else:
            print(f"   ❌ C++ Error: {res.status_code}")
    except Exception as e:
        print(f"   ❌ C++ Connection Error: {e}")

if __name__ == "__main__":
    inspect_system()
