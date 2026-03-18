from ...brain.memory.episodic.episodic_memory import EpisodicMemory
from ...agents.registry.manager import AgentRegistry

class CoordinationEngine:
    def __init__(self, episodic_memory: EpisodicMemory, agent_registry: AgentRegistry):
        self.episodic = episodic_memory
        self.registry = agent_registry

    def discover_shared_insights(self, query, exclude_agent_id=None):
        """
        Queries all 'shared' memories to find insights from other agents.
        """
        # We can reuse the episodic search with a special condition or just filter results
        # For now, let's use search with agent_id='coordination' which should see all shared
        results = self.episodic.search(user_id="*", query=query, agent_id="coordination", limit=10)
        
        # Filter: only keep shared memories, and optionally exclude the calling agent
        insights = []
        for r in results:
            if r.get("memory_type") == "shared":
                if exclude_agent_id and r.get("agent_id") == exclude_agent_id:
                    continue
                insights.append(r)
        
        return insights

    def broadcast_insight(self, agent_id, user_id, content, importance=9.0):
        """
        Explicitly stores an insight as 'shared' for other agents to see.
        """
        event = {
            "agent_id": agent_id,
            "user_id": user_id,
            "content": f"[Insight] {content}",
            "timestamp": time.time() if "time" not in globals() else __import__('time').time(),
            "importance": importance,
            "memory_type": "shared",
            "schema_tags": ["insight", "coordination"]
        }
        self.episodic.store(event)
        return event
