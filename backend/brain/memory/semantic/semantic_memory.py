import requests
import numpy as np
from ...models.model_router import ModelRouter

class SemanticMemory:
    def __init__(self, infra_url="http://localhost:8080"):
        self.infra_url = infra_url
        self.router = ModelRouter()

    def _get_embedding(self, text):
        vec = self.router.get_embedding(text)
        if not vec:
            return [0.0] * 384 # Fallback
        
        # Normalize for dot-product similarity in C++
        v = np.array(vec)
        norm = np.linalg.norm(v)
        if norm > 1e-6:
            v = v / norm
        return v.tolist()

    def store(self, user_id, text, timestamp, importance=5, agent_id="default_agent", memory_type="private", skip_llm=False, sqlite_id=None):
        vector = self._get_embedding(text)
        # Added sqlite_id to the metadata string for perfect resolution
        mem_id = f"{user_id}::{agent_id}::{memory_type}::{timestamp}::{sqlite_id}"
        payload = {"id": mem_id, "vector": vector}
        try:
            requests.post(f"{self.infra_url}/add_vector", json=payload)
        except Exception as e:
            print(f"Error connecting to C++ infra: {e}")

    def search(self, user_id, query, top_k=5):
        vector = self._get_embedding(query)
        payload = {"query": vector, "top_k": top_k}
        try:
            res = requests.post(f"{self.infra_url}/search_vector", json=payload)
            if res.status_code == 200:
                results = res.json().get("results", [])
                parsed_results = []
                query_words = set(query.lower().split())

                for item in results:
                    mid = item.get("id")
                    if not mid: continue
                    parts = mid.split("::")
                    if len(parts) >= 4:
                        m_user_id = parts[0]
                        # SECURITY: Only return memories for this user
                        if m_user_id != user_id:
                            continue
                            
                        # Hybrid Scoring: Boost results with exact keyword matches
                        # (Especially important for IDs like 'Galaxy X-76')
                        boost = 0.0
                        # Check for keyword matches in the memory metadata/id
                        for word in query_words:
                            if len(word) > 2 and word in mid.lower():
                                boost += 0.2
                            
                        parsed_results.append({
                            "id": mid,
                            "user_id": m_user_id,
                            "agent_id": parts[1],
                            "memory_type": parts[2],
                            "timestamp": parts[3],
                            "sqlite_id": parts[4] if len(parts) > 4 else None,
                            "score": item.get("score", 0) + boost
                        })
                
                # Re-sort by boosted score
                parsed_results.sort(key=lambda x: x["score"], reverse=True)
                return parsed_results
        except Exception as e:
            print(f"Error connecting to C++ infra: {e}")
        return []
