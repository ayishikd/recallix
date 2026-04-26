class MemoryRouter:
    def __init__(self, memory_manager):
        self.memory = memory_manager

    def route_retrieval(self, plan, user_id, agent_id="default_agent"):
        """
        Executes the retrieval plan by calling the appropriate memory sub-engines.
        """
        results = {
            "episodic": [],
            "semantic": [],
            "graph": [],
            "long_term": [],
            "insights": [],
            "learning_history": []
        }

        memory_types = plan.get("memory_types", [])
        top_k = plan.get("top_k", 5)
        queries = plan.get("vector_queries", [])
        primary_query = queries[0] if queries else ""

        # 1. Episodic Retrieval
        if "episodic" in memory_types or "recent_episodic" in memory_types:
            limit = 3 if "recent_episodic" in memory_types else top_k
            results["episodic"] = self.memory.episodic.search(
                user_id, 
                primary_query, 
                agent_id=agent_id,
                limit=limit
            )

        # 2. Semantic Retrieval
        if "semantic" in memory_types or "learning_history" in memory_types:
            semantic_candidates = self.memory.semantic.search(
                user_id, 
                primary_query, 
                top_k=top_k
            )
            # Filter and resolve content from Episodic Memory
            resolved = []
            for c in semantic_candidates:
                if c.get("agent_id") == agent_id or c.get("memory_type") == "shared":
                    # Fetch content from episodic memory using the timestamp as a proxy for the ID
                    # In a real system, we'd use the full UUID
                    ts = c.get("timestamp")
                    if ts:
                        episodic_match = self.memory.episodic.get_by_timestamp(user_id, ts)
                        if episodic_match:
                            c["content"] = episodic_match["content"]
                            c["importance"] = episodic_match["importance"]
                    resolved.append(c)
            
            if "semantic" in memory_types:
                results["semantic"] = resolved
            if "learning_history" in memory_types:
                results["learning_history"].extend(resolved)

        # 3. Knowledge Graph Expansion
        if "knowledge_graph" in memory_types or plan.get("graph_expansion_depth", 0) > 0:
            import requests
            try:
                # Use the primary query as the starting node for expansion
                res = requests.get(f"http://localhost:8080/get_neighbors?id={primary_query}")
                if res.status_code == 200:
                    results["graph"] = res.json() # C++ returns a JSON array
            except:
                pass

        # 4. Long Term / Insight retrieval
        if "long_term" in memory_types:
            # In MemoryOS, long_term is a capped store for high-importance items
            results["long_term"] = self.memory.long_term.get(user_id)
            
        if "insight" in memory_types:
            results["insights"] = self.memory.reflective.get_reflections(user_id, limit=3)

        return results
