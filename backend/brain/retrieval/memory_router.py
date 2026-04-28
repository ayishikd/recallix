class MemoryRouter:
    def __init__(self, memory_manager):
        self.memory = memory_manager

    def route_retrieval(self, plan, user_id, agent_id="default_agent"):
        results = {"episodic": [], "semantic": [], "graph": [], "long_term": [], "insights": []}
        memory_types = plan.get("memory_types", [])
        top_k = plan.get("top_k", 5)
        queries = plan.get("vector_queries", [])
        primary_query = queries[0] if queries else ""

        # 1. Episodic Retrieval
        if "episodic" in memory_types or "recent_episodic" in memory_types:
            limit = 3 if "recent_episodic" in memory_types else top_k
            results["episodic"] = self.memory.episodic.search(user_id, primary_query, agent_id=agent_id, limit=limit)

        # 2. Semantic Retrieval
        if "semantic" in memory_types:
            semantic_candidates = self.memory.semantic.search(user_id, primary_query, top_k=max(top_k * 3, 20))
            resolved = []
            for c in semantic_candidates:
                if c.get("agent_id") == agent_id or c.get("memory_type") == "shared":
                    # Use the explicit sqlite_id for perfect resolution, fallback to timestamp
                    sq_id = c.get("sqlite_id")
                    episodic_match = None
                    if sq_id and sq_id != "None":
                        episodic_match = self.memory.episodic.get_by_id(user_id, int(sq_id))
                    
                    if not episodic_match:
                        ts = c.get("timestamp")
                        if ts: episodic_match = self.memory.episodic.get_by_timestamp(user_id, ts)
                    
                    if episodic_match:
                        c["content"] = episodic_match["content"]
                        c["importance"] = episodic_match.get("importance", 5.0)
                        resolved.append(c)
            results["semantic"] = resolved

        return results
