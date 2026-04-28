import numpy as np
from backend.brain.models.model_router import ModelRouter
from backend.utils.internal_client import internal_post

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

    def store(self, user_id, text, timestamp, importance=5.0, agent_id="default_agent", memory_type="private", skip_llm=False, sqlite_id=None):
        vector = self._get_embedding(text)
        mem_id = f"{user_id}::{agent_id}::{memory_type}::{timestamp}::{importance}::{sqlite_id}"
        payload = {"id": mem_id, "vector": vector}
        try:
            internal_post(f"{self.infra_url}/add_vector", payload)
        except Exception as e:
            print(f"Error connecting to C++ infra: {e}")

    def search(self, user_id, query, top_k=5):
        vector = self._get_embedding(query)
        payload = {"query": vector, "top_k": top_k}
        try:
            res = internal_post(f"{self.infra_url}/search_vector", payload)
            if res.status_code == 200:
                results = res.json().get("results", [])
                parsed_results = []
                query_words = set(query.lower().split())

                for item in results:
                    mid = item.get("id")
                    if not mid: continue
                    parts = mid.split("::")
                    if len(parts) >= 5:
                        m_user_id = parts[0]
                        if m_user_id != user_id:
                            continue
                        
                        m_agent_id = parts[1]
                        m_type = parts[2]
                        m_ts = parts[3]
                        m_importance = float(parts[4])
                        m_sqlite_id = parts[5] if len(parts) > 5 else None

                        boost = 0.0
                        for word in query_words:
                            if len(word) > 2 and word in mid.lower():
                                boost += 0.1
                        
                        final_score = item.get("score", 0) + (m_importance / 100.0) + boost
                            
                        parsed_results.append({
                            "id": mid,
                            "user_id": m_user_id,
                            "agent_id": m_agent_id,
                            "memory_type": m_type,
                            "timestamp": m_ts,
                            "sqlite_id": m_sqlite_id,
                            "importance": m_importance,
                            "score": final_score
                        })
                
                parsed_results.sort(key=lambda x: x["score"], reverse=True)
                return parsed_results
        except Exception as e:
            print(f"Error connecting to C++ infra: {e}")
        return []

    def clear(self):
        try:
            internal_post(f"{self.infra_url}/clear", {})
        except: pass

    def compute_similarity(self, query, text):
        """Compute cosine similarity between query and target text."""
        q_vec = self._get_embedding(query)
        t_vec = self._get_embedding(text)
        
        # Dot product of normalized vectors = Cosine Similarity
        return np.dot(q_vec, t_vec)
