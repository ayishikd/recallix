from .client import MemoryClient
from typing import Dict, Any, List

class Memory:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        self.client = MemoryClient(api_key, base_url)

    def store(self, content: str, metadata: Dict = None) -> Dict[str, Any]:
        """Stores a new memory event."""
        return self.client.request("POST", "/memory/store", data={"content": content, "metadata": metadata})

    def recall(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Retrieves relevant memories based on a query."""
        return self.client.request("POST", "/memory/recall", data={"query": query, "limit": limit})

    def timeline(self) -> Dict[str, Any]:
        """Retrieves the chronological event timeline."""
        return self.client.request("GET", "/memory/timeline")

    def insights(self) -> Dict[str, Any]:
        """Retrieves reflection-based insights."""
        return self.client.request("GET", "/memory/insights")

    def profile(self) -> Dict[str, Any]:
        """Retrieves the user's cognitive profile summary."""
        return self.client.request("GET", "/memory/profile")
