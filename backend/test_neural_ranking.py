import requests
import time
import json

BRAIN_URL = "http://localhost:8000"

def wait_for_server(url, timeout=300):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            requests.get(url + "/docs")
            print("Server is ready!")
            return True
        except requests.exceptions.ConnectionError:
            time.sleep(5)
            print("Waiting for server to start (model download may be in progress)...")
    return False

def test_neural_ranking():
    if not wait_for_server(BRAIN_URL):
        print("Server failed to start in time.")
        return
        
    user_id = "user_ranking_test"
    
    print("\n--- Phase 1: Storing Diverse Memories ---")
    memories = [
        {"content": "I am working on a complex project involving AI memory systems.", "importance": None},
        {"content": "I like to eat pizza on Fridays.", "importance": None},
        {"content": "My goal is to achieve sub-second latency for neural reranking.", "importance": 10},
        {"content": "The weather today is quite cloudy.", "importance": 2}
    ]
    
    for mem in memories:
        print(f"Storing: {mem['content']}")
        for _ in range(3): # Retry up to 3 times
            res = requests.post(f"{BRAIN_URL}/memory/store", json={"user_id": user_id, "message": mem['content']})
            if res.status_code == 200:
                break
            print(f"Retrying store due to: {res.status_code}")
            time.sleep(2)
        if res.status_code != 200:
            print(f"Error storing: {res.text}")
        time.sleep(1)

    print("\n--- Phase 2: Neural Reranking Verification ---")
    query = "performance and speed in AI ranking"
    print(f"Query: {query}")
    
    res = requests.get(f"{BRAIN_URL}/memory/retrieve", params={"user_id": user_id, "query": query})
    if res.status_code == 200:
        data = res.json()
        # print(f"Raw Response: {json.dumps(data, indent=2)}") # Debug
        print(f"Prediction (Topic): {data.get('prediction', {}).get('topic')}")
        
        final = data.get("final_memories", [])
        print(f"\nFinal Ranked Memories (Top {len(final)}):")
        for i, m in enumerate(final):
            content = m.get("content", "N/A")
            score = m.get("attention_score", 0.0)
            rerank = m.get("rerank_score", 0.0)
            imp = m.get("importance", 0.0)
            print(f"{i+1}. [{content[:50]}...] | Score: {score:.4f} | Rerank: {rerank:.4f} | Imp: {imp}")
    else:
        print(f"Error retrieving: {res.text}")

if __name__ == "__main__":
    print("Verifying Neural Memory Importance Ranking and Reranking...")
    test_neural_ranking()
