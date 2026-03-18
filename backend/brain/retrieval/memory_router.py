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
            # Filter and add to appropriate bucket
            filtered = [c for c in semantic_candidates if c.get("agent_id") == agent_id or c.get("memory_type") == "shared"]
            if "semantic" in memory_types:
                results["semantic"] = filtered
            if "learning_history" in memory_types:
                results["learning_history"].extend(filtered)

        # 3. Knowledge Graph Expansion
        if "knowledge_graph" in memory_types or plan.get("graph_expansion_depth", 0) > 0:
            # Placeholder for graph retrieval logic
            # Typically looks up entities from context in a graph DB
            pass

        # 4. Long Term / Insight retrieval
        if "long_term" in memory_types:
            # In MemoryOS, long_term is a capped store for high-importance items
            results["long_term"] = self.memory.long_term.get(user_id)
            
        if "insight" in memory_types:
            results["insights"] = self.memory.reflective.get_reflections(user_id, limit=3)

        return results
