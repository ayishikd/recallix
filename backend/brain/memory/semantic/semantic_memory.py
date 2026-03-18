import requests
import numpy as np

class SemanticMemory:
    def __init__(self, infra_url="http://localhost:8080"):
        self.infra_url = infra_url
        # In a real app, use a proper embedding model
        # For now, we'll use a dummy embedding or mock it

    def _get_embedding(self, text):
        # Mock embedding: normalized random vector
        vec = np.random.rand(128).astype(np.float32)
        return (vec / np.linalg.norm(vec)).tolist()

    def store(self, user_id, text, timestamp, importance=5, agent_id="default_agent", memory_type="private"):
        vector = self._get_embedding(text)
        # Include agent and type in the ID for filtering since C++ mock is simple
        mem_id = f"{user_id}::{agent_id}::{memory_type}::{timestamp}"
        payload = {
            "id": mem_id,
            "vector": vector
        }
        try:
            requests.post(f"{self.infra_url}/add_vector", json=payload)
            # Index with default access count 1
            idx_payload = {
                "id": mem_id,
                "importance": importance,
                "access_count": 1
            }
            requests.post(f"{self.infra_url}/index_memory", json=idx_payload)
        except Exception as e:
            print(f"Error connecting to C++ infra: {e}")

    def search(self, user_id, query, top_k=5):
        vector = self._get_embedding(query)
        payload = {
            "query": vector,
            "top_k": top_k
        }
        try:
            res = requests.post(f"{self.infra_url}/search_vector", json=payload)
            if res.status_code == 200:
                results = res.json().get("results", [])
                parsed_results = []
                for mid in results:
                    parts = mid.split("::")
                    if len(parts) >= 4:
                        parsed_results.append({
                            "id": mid,
                            "user_id": parts[0],
                            "agent_id": parts[1],
                            "memory_type": parts[2],
                            "timestamp": parts[3]
                        })
                return parsed_results
        except Exception as e:
            print(f"Error connecting to C++ infra: {e}")
        return []
