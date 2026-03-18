export interface MemoryConfig {
    apiKey: string;
    baseUrl?: string;
}

export class MemoryClient {
    private apiKey: string;
    private baseUrl: string;

    constructor(config: MemoryConfig) {
        this.apiKey = config.apiKey;
        this.baseUrl = (config.baseUrl || "http://localhost:8000").replace(/\/$/, "");
    }

    async request<T>(method: string, endpoint: string, data?: any): Promise<T> {
        const url = `${this.baseUrl}${endpoint}`;
        try {
            const response = await fetch(url, {
                method,
                headers: {
                    "X-API-Key": this.apiKey,
                    "Content-Type": "application/json"
                },
                body: data ? JSON.stringify(data) : undefined
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.statusText}`);
            }

            return await response.json();
        } catch (error: any) {
            return {
                status: "error",
                message: error.message,
                code: "SDK_ERROR"
            } as any;
        }
    }
}
