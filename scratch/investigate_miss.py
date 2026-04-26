import requests
import json

API_URL = "http://127.0.0.1:8000/memory"
API_KEY = "local_dev_key"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

def investigate_miss():
    query = "When is the anniversary date?"
    payload = {"query": query}
    
    print(f"🔍 Investigating retrieval for: '{query}'")
    res = requests.post(f"{API_URL}/recall", json=payload, headers=HEADERS)
    
    if res.status_code == 200:
        data = res.json()["data"]
        memories = data.get("memories", [])
        print(f"\n✅ Retrieval successful. Found {len(memories)} memories.")
        
        for i, m in enumerate(memories):
            content = m if isinstance(m, str) else m.get("content", "")
            print(f"   [{i}] Content: {content}")
            if "score" in m: print(f"       Score: {m['score']}")
            if "rerank_score" in m: print(f"       Rerank Score: {m['rerank_score']}")
        
        print("\n🛠️ Retrieval Plan used:")
        print(json.dumps(data.get("retrieval_plan", {}), indent=2))
        
        print("\n📈 Latency: ", data.get("latency_ms"), "ms")
    else:
        print(f"❌ Error: {res.status_code}")
        print(res.text)

if __name__ == "__main__":
    investigate_miss()
