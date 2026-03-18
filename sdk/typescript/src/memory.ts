import { MemoryClient, MemoryConfig } from "./client";

export class Memory {
    private client: MemoryClient;

    constructor(config: MemoryConfig) {
        this.client = new MemoryClient(config);
    }

    async store(content: string, metadata?: Record<string, any>) {
        return this.client.request("POST", "/memory/store", { content, metadata });
    }

    async recall(query: string, limit: number = 10) {
        return this.client.request("POST", "/memory/recall", { query, limit });
    }

    async timeline() {
        return this.client.request("GET", "/memory/timeline");
    }

    async insights() {
        return this.client.request("GET", "/memory/insights");
    }

    async profile() {
        return this.client.request("GET", "/memory/profile");
    }
}
