class RetrievalPlanner:
    def __init__(self):
        pass

    def generate_plan(self, context, query, agent_id="default_agent"):
        """
        Converts inferred context into a specific multi-engine retrieval plan.
        """
        # 1. Vector Search Plan (Query variations)
        vector_queries = [query]
        if context["topic"] != "general":
            vector_queries.append(f"{context['topic']} {context['domain']}")
            vector_queries.append(f"concepts related to {context['topic']}")

        # 2. Graph Expansion Plan
        graph_depth = 1
        if context["user_state"] in ["learning", "research"]:
            graph_depth = 2

        # 3. Filtering Logic
        importance_min = 4.0
        if context["user_state"] == "preference_update":
            importance_min = 6.0
        elif context["user_state"] == "conversation":
            importance_min = 2.0

        filters = {
            "agent_id": agent_id,
            "importance_min": importance_min,
            "domain": context["domain"]
        }
        
        return {
            "vector_queries": vector_queries,
            "graph_expansion_depth": graph_depth,
            "memory_filters": filters,
            "memory_types": context["memory_types"],
            "top_k": 100 if context["user_state"] in ["research", "learning"] else 50
        }
