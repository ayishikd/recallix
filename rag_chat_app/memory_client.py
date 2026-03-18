import requests

class MemoryOSClient:
    def __init__(self, api_key, base_url="http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {"X-API-Key": api_key}

    def _request(self, method, endpoint, data=None):
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "POST":
                res = requests.post(url, json=data, headers=self.headers)
            else:
                res = requests.get(url, headers=self.headers)
            return res.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # Public Endpoints
    def store(self, content):
        return self._request("POST", "/memory/store", {"content": content})

    def recall(self, query):
        return self._request("POST", "/memory/recall", {"query": query})

    def get_timeline(self):
        return self._request("GET", "/memory/timeline")

    def get_insights(self):
        return self._request("GET", "/memory/insights")

    def get_world_state(self):
        return self._request("GET", "/memory/world-state")

    def get_stats(self):
        return self._request("GET", "/memory/stats")

    # Multi-Agent Endpoints
    def agent_store(self, content, agent_id, memory_type="private"):
        return self._request("POST", "/agents/store", {
            "content": content,
            "agent_id": agent_id,
            "memory_type": memory_type
        })

    def agent_recall(self, query, agent_id):
        return self._request("POST", "/agents/recall", {
            "query": query,
            "agent_id": agent_id
        })

    def list_agents(self):
        return self._request("GET", "/agents/list")

    def list_schemas(self):
        return self._request("GET", "/agents/schemas")

    def get_profile(self):
        return self._request("GET", "/memory/profile")
