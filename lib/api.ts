const API_BASE = "http://localhost:8000";
const API_KEY = "local_dev_key";

const headers = () => ({
    "Content-Type": "application/json",
    "X-API-Key": API_KEY,
});

async function api<T = any>(method: string, path: string, body?: any): Promise<{ status: string; data: T; timestamp: string }> {
    try {
        const res = await fetch(`${API_BASE}${path}`, {
            method,
            headers: headers(),
            body: body ? JSON.stringify(body) : undefined,
        });
        return res.json();
    } catch (e: any) {
        return { status: "error", data: null as any, timestamp: new Date().toISOString() };
    }
}

export const memoryApi = {
    store: (content: string) => api("POST", "/memory/store", { content }),
    recall: (query: string, limit = 10) => api("POST", "/memory/recall", { query, limit }),
    timeline: () => api<any[]>("GET", "/memory/timeline"),
    insights: () => api<any[]>("GET", "/memory/insights"),
    worldState: () => api<Record<string, any>>("GET", "/memory/world-state"),
    metaInsights: () => api<any[]>("GET", "/memory/meta-insights"),
    stats: () => api<{ episodic_memories: number; timeline_events: number; reflections: number; schemas: number; active_agents: number }>("GET", "/memory/stats"),
    systemStats: () => api<{ total_nodes: number; pending_nodes: number; max_layer: number; M: number; efConstruction: number; efSearch: number }>("GET", "/memory/system/stats"),
    profile: () => api<any>("GET", "/memory/profile"),
};

export const agentApi = {
    store: (agentId: string, content: string, memoryType = "private") =>
        api("POST", "/agents/store", { agent_id: agentId, content, memory_type: memoryType }),
    recall: (agentId: string, query: string, limit = 10) =>
        api("POST", "/agents/recall", { agent_id: agentId, query, limit }),
    list: () => api<any[]>("GET", "/agents/list"),
    schemas: () => api<any[]>("GET", "/agents/schemas"),
};
