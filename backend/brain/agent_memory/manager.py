from backend.brain.memory.episodic.episodic_memory import EpisodicMemory
from backend.agents.registry.manager import AgentRegistry
import time

class AgentMemoryManager:
    def __init__(self, episodic_memory: EpisodicMemory, agent_registry: AgentRegistry):
        self.episodic = episodic_memory
        self.registry = agent_registry

    def store_memory(self, agent_id, user_id, content, memory_type="private", importance=1.0, schema_tags=None):
        """
        Stores a memory for a specific agent.
        """
        event = {
            "agent_id": agent_id,
            "user_id": user_id,
            "content": content,
            "timestamp": time.time(),
            "importance": importance,
            "memory_type": memory_type,
            "schema_tags": schema_tags
        }
        self.episodic.store(event)
        return event

    def retrieve_memory(self, agent_id, user_id, query, limit=5):
        """
        Retrieves memories accessible to the agent (private + shared).
        """
        return self.episodic.search(user_id, query, agent_id=agent_id, limit=limit)

    def share_memory(self, memory_id, target_agent_id=None):
        """
        Promotes a private memory to 'shared' type.
        If target_agent_id is provided, it could be a scoped share (future implementation).
        For now, simply set memory_type to 'shared'.
        """
        # This would require an update method in EpisodicMemory
        # I'll add an update method to EpisodicMemory if needed later.
        pass
