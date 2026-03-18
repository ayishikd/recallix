import os
from sentence_transformers import CrossEncoder

class NeuralReranker:
    def __init__(self, model_name="BAAI/bge-reranker-base", cache_dir="backend/models/reranker"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        # Load the model locally
        self.model = CrossEncoder(model_name, device="cpu", cache_folder=self.cache_dir)

    def rerank(self, query, candidates, top_n=20):
        """
        Reranks a list of candidate memories based on the query.
        Each candidate should be a dict with a 'content' field.
        """
        if not candidates:
            return []

        # Prepare pairs for the cross-encoder
        pairs = [[query, c.get("content", "")] for c in candidates]
        
        # Compute relevance scores
        scores = self.model.predict(pairs)
        
        # Attach scores to candidates
        for i, candidate in enumerate(candidates):
            candidate["rerank_score"] = float(scores[i])
            
        # Sort by rerank_score descending
        candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
        
        return candidates[:top_n]
