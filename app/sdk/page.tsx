"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Code2, Terminal, Copy, Check, ArrowLeft, Brain } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";

const CodeBlock = ({ code, language }: { code: string; language: string }) => {
    const [copied, setCopied] = useState(false);
    const handleCopy = () => { navigator.clipboard.writeText(code); setCopied(true); setTimeout(() => setCopied(false), 2000); };
    return (
        <div className="relative group rounded-2xl overflow-hidden border border-white/5 bg-zinc-950/50 backdrop-blur-xl">
            <div className="flex items-center justify-between px-5 py-2.5 border-b border-white/5 bg-white/5">
                <div className="flex items-center gap-2">
                    <Terminal className="w-3.5 h-3.5 text-zinc-500" />
                    <span className="text-[10px] font-black uppercase tracking-widest text-zinc-500">{language}</span>
                </div>
                <button onClick={handleCopy} className="p-1.5 hover:bg-white/5 rounded-lg transition-colors text-zinc-500 hover:text-white">
                    {copied ? <Check className="w-3.5 h-3.5 text-green-400" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
            </div>
            <div className="p-5 overflow-x-auto custom-scrollbar">
                <pre className="text-sm font-mono leading-relaxed text-zinc-300"><code>{code}</code></pre>
            </div>
        </div>
    );
};

export default function SDKPage() {
    const pythonCode = `from memoryos import Memory

# Initialize with your API key
memory = Memory(api_key="local_dev_key")

# Store a memory event
memory.store("User is studying recursive algorithms.")

# Recall semantically related context
results = memory.recall("What is the user learning?")
print(results)

# Fetch the chronological timeline
timeline = memory.timeline()

# Get AI-generated reflection insights
insights = memory.insights()

# Get the user's cognitive profile
profile = memory.profile()`;

    const tsCode = `import { Memory } from "memoryos-sdk";

// Initialize the client
const memory = new Memory({
  apiKey: "local_dev_key",
  baseUrl: "http://localhost:8000"
});

// Store an event
await memory.store("User studying recursion");

// Perform semantic recall
const results = await memory.recall("learning");

// Access reflection insights
const insights = await memory.insights();

// Get full cognitive profile
const profile = await memory.profile();`;

    const curlCode = `# Store a memory
curl -X POST http://localhost:8000/memory/store \\
  -H "X-API-Key: local_dev_key" \\
  -H "Content-Type: application/json" \\
  -d '{"content": "User is studying ML"}'

# Recall context
curl -X POST http://localhost:8000/memory/recall \\
  -H "X-API-Key: local_dev_key" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "learning", "limit": 5}'

# Get timeline
curl -H "X-API-Key: local_dev_key" \\
  http://localhost:8000/memory/timeline

# Get system stats
curl -H "X-API-Key: local_dev_key" \\
  http://localhost:8000/memory/stats`;

    return (
        <div className="min-h-screen bg-black text-white selection:bg-cyan-500/30">
            <nav className="fixed top-0 left-0 right-0 z-50 h-14 border-b border-white/5 flex items-center justify-between px-6 glass backdrop-blur-2xl">
                <div className="flex items-center gap-4">
                    <Link href="/" className="flex items-center gap-2 text-zinc-400 hover:text-white transition-colors">
                        <ArrowLeft className="w-4 h-4" /> <Brain className="w-5 h-5 text-cyan-400" />
                    </Link>
                    <span className="text-sm font-black tracking-tight">DEVELOPER HUB</span>
                </div>
                <Link href="/playground"><Button variant="ghost" size="sm" className="text-zinc-500 hover:text-white text-xs font-bold">Live Playground</Button></Link>
            </nav>

            <main className="pt-28 pb-24 container mx-auto px-6 max-w-5xl">
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-16 text-center">
                    <Badge className="mb-6 py-2 px-4 bg-cyan-500/10 border-cyan-500/20 text-cyan-400 rounded-full font-bold border">v1.0.0</Badge>
                    <h1 className="text-5xl md:text-7xl font-black tracking-tighter mb-6 leading-tight">
                        The Memory SDK<br /><span className="text-gradient">for AI Agents.</span>
                    </h1>
                    <p className="text-lg text-zinc-500 font-bold max-w-2xl mx-auto leading-relaxed">
                        Give your agents permanent cognitive memory with a single line of code. All processing runs locally on your infrastructure.
                    </p>
                </motion.div>

                {/* API Endpoints Reference */}
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="mb-16">
                    <h2 className="text-2xl font-black tracking-tight mb-6">API Endpoints</h2>
                    <div className="glass-card rounded-2xl overflow-hidden">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b border-white/5">
                                    <th className="text-left px-5 py-3 text-[10px] font-black uppercase tracking-widest text-zinc-500">Method</th>
                                    <th className="text-left px-5 py-3 text-[10px] font-black uppercase tracking-widest text-zinc-500">Endpoint</th>
                                    <th className="text-left px-5 py-3 text-[10px] font-black uppercase tracking-widest text-zinc-500">Description</th>
                                </tr>
                            </thead>
                            <tbody>
                                {[
                                    ["POST", "/memory/store", "Store a new memory event"],
                                    ["POST", "/memory/recall", "Semantic recall with neural reranking"],
                                    ["GET", "/memory/timeline", "Chronological event history"],
                                    ["GET", "/memory/insights", "AI-generated reflection insights"],
                                    ["GET", "/memory/world-state", "Inferred hidden user states"],
                                    ["GET", "/memory/meta-insights", "Meta-memory optimization logs"],
                                    ["GET", "/memory/stats", "System-wide memory statistics"],
                                    ["GET", "/memory/profile", "User cognitive profile summary"],
                                ].map(([method, path, desc]) => (
                                    <tr key={path} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                                        <td className="px-5 py-3"><Badge className={`text-[10px] font-black ${method === "POST" ? "bg-cyan-500/10 text-cyan-400 border-cyan-500/20" : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"}`}>{method}</Badge></td>
                                        <td className="px-5 py-3 font-mono text-xs text-zinc-300">{path}</td>
                                        <td className="px-5 py-3 text-xs font-bold text-zinc-500">{desc}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </motion.div>

                {/* Code Examples */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16">
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="space-y-4">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center"><Code2 className="w-5 h-5 text-blue-400" /></div>
                            <h2 className="text-xl font-black tracking-tight">Python SDK</h2>
                        </div>
                        <CodeBlock code={pythonCode} language="python" />
                    </motion.div>
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="space-y-4">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center"><Code2 className="w-5 h-5 text-cyan-400" /></div>
                            <h2 className="text-xl font-black tracking-tight">TypeScript SDK</h2>
                        </div>
                        <CodeBlock code={tsCode} language="typescript" />
                    </motion.div>
                </div>

                {/* cURL Examples */}
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="mb-16 space-y-4">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center"><Terminal className="w-5 h-5 text-orange-400" /></div>
                        <h2 className="text-xl font-black tracking-tight">cURL / REST API</h2>
                    </div>
                    <CodeBlock code={curlCode} language="bash" />
                </motion.div>

                {/* Auth Info */}
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
                    <div className="bg-zinc-900/50 rounded-[32px] border border-white/5 p-8 md:p-12 relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/5 blur-[80px] rounded-full" />
                        <h2 className="text-2xl font-black tracking-tighter mb-8 relative z-10">Configuration</h2>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative z-10">
                            <div>
                                <div className="text-[10px] font-black uppercase tracking-widest text-cyan-400 mb-2">Authentication</div>
                                <p className="text-zinc-400 text-sm font-bold leading-relaxed">
                                    All requests require an <code className="text-cyan-400 bg-cyan-500/10 px-1.5 py-0.5 rounded text-xs">X-API-Key</code> header. Default dev key: <code className="text-white bg-zinc-800 px-1.5 py-0.5 rounded text-xs">local_dev_key</code>
                                </p>
                            </div>
                            <div>
                                <div className="text-[10px] font-black uppercase tracking-widest text-cyan-400 mb-2">Base URL</div>
                                <p className="text-zinc-400 text-sm font-bold leading-relaxed">
                                    Backend runs on <code className="text-white bg-zinc-800 px-1.5 py-0.5 rounded text-xs">http://localhost:8000</code>. All endpoints are prefixed with <code className="text-cyan-400 bg-cyan-500/10 px-1.5 py-0.5 rounded text-xs">/memory</code>
                                </p>
                            </div>
                            <div>
                                <div className="text-[10px] font-black uppercase tracking-widest text-cyan-400 mb-2">Local Models</div>
                                <p className="text-zinc-400 text-sm font-bold leading-relaxed">
                                    Requires <code className="text-white bg-zinc-800 px-1.5 py-0.5 rounded text-xs">ollama serve</code> with Mistral and Llama 3.1 models pulled locally.
                                </p>
                            </div>
                        </div>
                    </div>
                </motion.div>
            </main>
        </div>
    );
}
