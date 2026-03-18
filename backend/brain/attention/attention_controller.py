class AttentionController:
    def __init__(self, weights=None, policy_path="backend/storage/memory_policies.json"):
        import json
        import os
        # Default weights for different attention signals
        self.weights = weights or {
            "semantic_similarity": 1.0,
            "importance": 0.8,
            "recency": 0.6,
            "cluster_relevance": 0.7,
            "schema_relevance": 0.5,
            "prediction_score": 0.9,
            "state_relevance": 0.8
        }
        
        # Load from meta-memory policy if exists
        if os.path.exists(policy_path):
            try:
                with open(policy_path, 'r') as f:
                    policies = json.load(f)
                    if "importance_weights" in policies:
                        self.weights.update(policies["importance_weights"])
                        print(f"[AttentionController] Loaded dynamic weights: {policies['importance_weights']}")
            except:
                pass

    def score_memories(self, memories, contextual_signals):
        """
        Calculates attention scores for a list of memories based on multiple signals.
        final_score = reranker_score * importance * recency * prediction
        """
        import time
        scored_memories = []
        now = time.time()
        
        for memory in memories:
            # 1. Rerank Score (normalized or used directly)
            rerank_score = memory.get("rerank_score", 0.5)
            
            # 2. Intrinsic Importance (1-10 -> 0.1-1.0)
            importance = memory.get("importance", 5.0) / 10.0
            
            # 3. Recency (Decay)
            timestamp = memory.get("timestamp", now)
            hours_old = (now - timestamp) / 3600
            recency = 1.0 / (1.0 + hours_old) # Very simple decay
            
            # 4. Reinforcement Signal (Learn from usage)
            reinforcement = memory.get("reinforcement_score", 1.0)
            
            # 5. Prediction Match
            prediction_boost = 1.0
            predicted_topic = contextual_signals.get("topic", "")
            if predicted_topic and predicted_topic.lower() in memory.get("content", "").lower():
                prediction_boost = 1.5
            
            # Final Combined Score
            # final_score = reranker_score * importance * recency * reinforcement * prediction
            final_score = rerank_score * (importance * self.weights["importance"]) * \
                          (recency * self.weights["recency"]) * reinforcement * prediction_boost
            
            scored_memories.append({
                "memory": memory,
                "attention_score": final_score
            })
            
        scored_memories.sort(key=lambda x: x["attention_score"], reverse=True)
        return scored_memories

    def filter(self, scored_memories, top_n=10):
        """
        Returns only the top N memories that the AI should focus on.
        """
        return [m["memory"] for m in scored_memories[:top_n]]
