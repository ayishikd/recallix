"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Brain, Send, Database, Lightbulb, Clock,
    Search, ArrowLeft, Terminal, Layers, RefreshCw, Target
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { memoryApi, agentApi } from "@/lib/api";
import Link from "next/link";

interface Message { role: "user" | "assistant"; content: string }
interface TimelineEvent { content: string; timestamp: number }
interface Insight { summary: string; confidence: number; timestamp: number }
interface LogEntry { system: string; stage: string; detail: string; duration_ms: number }

const STAGES = ["Input", "Intent Engine", "Sensory", "Working", "Episodic", "Semantic", "Long-Term", "Reflection", "Meta"];

const systemColors: Record<string, { bg: string; text: string; border: string; label: string }> = {
    python: { bg: "bg-cyan-500/10", text: "text-cyan-400", border: "border-cyan-500/20", label: "PYTHON" },
    ollama: { bg: "bg-purple-500/10", text: "text-purple-400", border: "border-purple-500/20", label: "OLLAMA" },
    cpp: { bg: "bg-amber-500/10", text: "text-amber-400", border: "border-amber-500/20", label: "C++" },
};

type PlaygroundTab = "single" | "multi" | "ame";

export default function PlaygroundPage() {
    const [activeTab, setActiveTab] = useState<PlaygroundTab>("single");
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
    const [insights, setInsights] = useState<Insight[]>([]);
    const [recallResults, setRecallResults] = useState<any>({});
    const [processingLogs, setProcessingLogs] = useState<LogEntry[]>([]);
    const [activeStage, setActiveStage] = useState(-1);
    const [rightTab, setRightTab] = useState<"logs" | "timeline" | "insights" | "recall" | "schemas">("logs");

    // Multi-agent state
    const [agents, setAgents] = useState<any[]>([]);
    const [selectedAgent, setSelectedAgent] = useState("");
    const [memoryType, setMemoryType] = useState<"private" | "shared">("private");

    // AME state
    const [schemas, setSchemas] = useState<any[]>([]);

    const chatEnd = useRef<HTMLDivElement>(null);

    useEffect(() => { chatEnd.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

    useEffect(() => {
        loadInitialData();
    }, [activeTab]);

    const loadInitialData = async () => {
        if (activeTab === "multi") {
            const res = await agentApi.list();
            if (res.data) {
                setAgents(res.data);
                if (res.data.length > 0 && !selectedAgent) setSelectedAgent(res.data[0].agent_id);
            }
        } else if (activeTab === "ame") {
            const res = await agentApi.schemas();
            if (res.data) setSchemas(res.data);
            setRightTab("schemas");
        }
    };

    const refreshSidebar = async () => {
        const [tl, ins] = await Promise.all([memoryApi.timeline(), memoryApi.insights()]);
        if (tl.data) setTimeline(Array.isArray(tl.data) ? tl.data : []);
        if (ins.data) setInsights(Array.isArray(ins.data) ? ins.data : []);

        if (activeTab === "ame") {
            const sRes = await agentApi.schemas();
            if (sRes.data) setSchemas(sRes.data);
        }
    };

    const animatePipeline = async () => {
        for (let i = 0; i < STAGES.length; i++) {
            setActiveStage(i);
            await new Promise((r) => setTimeout(r, 200));
        }
        setTimeout(() => setActiveStage(-1), 500);
    };

    const handleSend = async () => {
        if (!input.trim() || loading) return;
        const msg = input.trim();
        setInput("");
        setMessages((m) => [...m, { role: "user", content: msg }]);
        setLoading(true);
        setProcessingLogs([]);
        if (rightTab !== "timeline" && rightTab !== "insights") setRightTab("logs");

        // Animate pipeline
        animatePipeline();

        // Store memory — route based on activeTab
        let storeRes;
        if (activeTab === "multi") {
            storeRes = await agentApi.store(selectedAgent, msg, memoryType);
        } else {
            storeRes = await memoryApi.store(msg);
        }

        const storeData = storeRes?.data || {};
        const logs: LogEntry[] = storeData.processing_log || [];
        setProcessingLogs(logs);

        // Recall related context
        let recallRes;
        if (activeTab === "multi") {
            recallRes = await agentApi.recall(selectedAgent, msg);
        } else {
            recallRes = await memoryApi.recall(msg);
        }

        const recallData = recallRes?.data || {};
        const finalMemories = recallData.memories || recallData.final_memories || [];
        setRecallResults(recallRes?.data || {}); // Store full recall data for richer visualization

        // Build response
        let response = `✅ Memory stored in ${storeData.total_ms || "—"}ms\n`;
        response += `• Importance: ${storeData.importance?.toFixed(1) || "—"}/10`;
        
        // Add Intent Info
        if (recallData.intent) {
            response += `\n• Detected Intent: **${recallData.intent.toUpperCase()}** (${(recallData.confidence * 100).toFixed(0)}%)`;
        }

        if (storeData.promoted) response += ` 🔥 PROMOTED!`;
        if (storeData.schemas?.length) response += `\n• Schemas: ${storeData.schemas.join(", ")}`;
        if (finalMemories.length > 0) {
            response += `\n• Recalled ${finalMemories.length} related context items`;
        }

        setMessages((m) => [...m, { role: "assistant", content: response }]);
        await refreshSidebar();
        setLoading(false);
    };

    return (
        <div className="h-screen bg-black text-white flex flex-col overflow-hidden">
            {/* Nav */}
            <nav className="shrink-0 h-14 border-b border-white/5 flex items-center justify-between px-6 glass backdrop-blur-2xl">
                <div className="flex items-center gap-4">
                    <Link href="/" className="flex items-center gap-2 text-zinc-400 hover:text-white transition-colors">
                        <ArrowLeft className="w-4 h-4" /> <Brain className="w-5 h-5 text-cyan-400" />
                    </Link>
                    <div className="h-4 w-px bg-white/10 mx-2" />
                    <div className="flex bg-zinc-900 rounded-lg p-1 border border-white/5">
                        {(["single", "multi", "ame"] as PlaygroundTab[]).map(t => (
                            <button
                                key={t}
                                onClick={() => { setActiveTab(t); setMessages([]); }}
                                className={`px-3 py-1 rounded-md text-[10px] font-black uppercase tracking-tight transition-all ${activeTab === t ? "bg-cyan-500 text-black shadow-lg shadow-cyan-500/20" : "text-zinc-500 hover:text-zinc-300"}`}
                            >
                                {t === "single" ? "Single Agent" : t === "multi" ? "Multi Agent" : "AME Evolution"}
                            </button>
                        ))}
                    </div>
                </div>
                <div className="flex items-center gap-3">
                    <Link href="/architecture"><Button variant="ghost" size="sm" className="text-zinc-500 hover:text-white text-[10px] font-black uppercase">Architecture</Button></Link>
                    <Link href="/observability"><Button variant="ghost" size="sm" className="text-zinc-500 hover:text-white text-[10px] font-black uppercase">Metrics</Button></Link>
                </div>
            </nav>

            {/* Pipeline Visualizer (Hidden in AME mode) */}
            {activeTab !== "ame" && (
                <div className="shrink-0 border-b border-white/5 bg-zinc-950/50 px-6 py-2">
                    <div className="flex items-center justify-center gap-1">
                        {STAGES.map((s, i) => (
                            <React.Fragment key={s}>
                                <motion.div
                                    animate={{
                                        backgroundColor: activeStage === i ? "rgba(34,211,238,0.2)" : "rgba(39,39,42,0.5)",
                                        borderColor: activeStage === i ? "rgba(34,211,238,0.5)" : "rgba(63,63,70,0.3)",
                                        scale: activeStage === i ? 1.05 : 1,
                                    }}
                                    className="px-2 py-1 rounded-md border text-[9px] font-black tracking-wide"
                                    style={{ color: activeStage === i ? "#22d3ee" : "#52525b" }}
                                >
                                    {s}
                                </motion.div>
                                {i < STAGES.length - 1 && (
                                    <div className={`w-3 h-px ${activeStage > i ? "bg-cyan-500/50" : "bg-zinc-800"}`} />
                                )}
                            </React.Fragment>
                        ))}
                    </div>
                </div>
            )}

            {/* Sub-nav for Multi-Agent */}
            {activeTab === "multi" && (
                <div className="shrink-0 bg-zinc-900/30 border-b border-white/5 px-6 py-2 flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        <span className="text-[10px] font-black text-zinc-500 uppercase tracking-widest">Selected Agent:</span>
                        <select
                            value={selectedAgent}
                            onChange={(e) => setSelectedAgent(e.target.value)}
                            className="bg-black border border-white/10 rounded-md px-2 py-1 text-[10px] font-bold text-cyan-400 focus:outline-none focus:border-cyan-500/50"
                        >
                            {agents.map(a => (
                                <option key={a.agent_id} value={a.agent_id}>{a.name} ({a.role})</option>
                            ))}
                        </select>
                    </div>
                    <div className="flex items-center gap-2 ml-auto">
                        <span className="text-[10px] font-black text-zinc-500 uppercase tracking-widest">Memory Type:</span>
                        <div className="flex bg-black rounded-md p-0.5 border border-white/10">
                            {["private", "shared"].map(t => (
                                <button
                                    key={t}
                                    onClick={() => setMemoryType(t as any)}
                                    className={`px-2 py-0.5 rounded text-[9px] font-black uppercase transition-all ${memoryType === t ? "bg-zinc-800 text-white" : "text-zinc-600 hover:text-zinc-400"}`}
                                >
                                    {t}
                                </button>
                            ))}
                        </div>
                        {memoryType === "shared" && <Badge className="bg-amber-500/10 text-amber-500 border-amber-500/20 text-[8px] px-1 animate-pulse">BROADCAST</Badge>}
                    </div>
                </div>
            )}

            {/* Main Content */}
            <div className="flex-1 flex overflow-hidden">
                {/* Chat / Dashboard */}
                <div className="flex-1 flex flex-col min-w-0 bg-zinc-950/20">
                    {activeTab === "ame" ? (
                        <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
                            <div className="max-w-4xl mx-auto">
                                <div className="flex items-center justify-between mb-8">
                                    <div>
                                        <h2 className="text-3xl font-black tracking-tight text-white mb-2">Autonomous Memory Evolution</h2>
                                        <p className="text-zinc-500 font-bold text-sm">The Meta-Memory worker is scanning your baseline memories to discover emergent conceptual schemas.</p>
                                    </div>
                                    <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 px-3 py-1 font-black tracking-widest animate-pulse">ACTIVE ANALYSIS</Badge>
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {schemas.length > 0 ? schemas.map((s, i) => (
                                        <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }} className="p-6 rounded-[24px] glass-card border-white/5 hover:border-emerald-500/20 transition-all group">
                                            <div className="flex items-center justify-between mb-4">
                                                <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                                                    <Layers className="w-5 h-5 text-emerald-400" />
                                                </div>
                                                <span className="text-[10px] font-black text-zinc-600 uppercase tracking-widest">Schema ID: {s.schema_id}</span>
                                            </div>
                                            <h3 className="text-lg font-black text-white mb-2 group-hover:text-emerald-400 transition-colors uppercase">{s.schema_id.replace(/_/g, ' ')}</h3>
                                            <div className="flex flex-wrap gap-2 mb-4">
                                                {s.fields?.map((f: string) => (
                                                    <Badge key={f} variant="outline" className="text-[9px] border-white/5 text-zinc-400">{f}</Badge>
                                                ))}
                                            </div>
                                            <p className="text-xs text-zinc-500 font-bold leading-relaxed">Discovered conceptually via pattern detection across {s.discover_count || 5}+ related episodic events.</p>
                                        </motion.div>
                                    )) : (
                                        <div className="col-span-full py-20 text-center border-2 border-dashed border-white/5 rounded-[32px]">
                                            <RefreshCw className="w-12 h-12 text-zinc-800 mx-auto mb-4 animate-spin-slow" />
                                            <p className="text-zinc-600 font-black">Waiting for evolution cycle...</p>
                                            <p className="text-zinc-700 text-xs font-bold mt-2">The system evolves when it detects high-density topic clusters.</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ) : (
                        <>
                            <div className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar">
                                {messages.length === 0 && (
                                    <div className="flex flex-col items-center justify-center h-full text-center">
                                        <div className="w-20 h-20 rounded-[32px] bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center mb-8">
                                            <Brain className="w-10 h-10 text-cyan-400" />
                                        </div>
                                        <h2 className="text-3xl font-black tracking-tight mb-2">
                                            {activeTab === "single" ? "Single Agent Playground" : "Multi-Agent Orchestrator"}
                                        </h2>
                                        <p className="text-zinc-500 font-bold max-w-md mb-6 leading-relaxed">
                                            {activeTab === "single"
                                                ? "Store and retrieve memories in the default cognitive space. Perfect for high-speed personal assistants."
                                                : "Test cross-agent boundaries. Share knowledge across the swarm or keep private logic isolated."}
                                        </p>
                                        <div className="flex flex-wrap gap-2 justify-center max-w-xl">
                                            {(activeTab === "single"
                                                ? ["I'm a senior software engineer", "Remember that I like sushi", "I store my logs in /var/logs", "My car is a Tesla"]
                                                : ["Researching quantum computing", "SHARED: Optimization complete", "SECRET: Root password is admin", "Broadcast the architecture update"]
                                            ).map((ex) => (
                                                <button key={ex} onClick={() => setInput(ex)} className="px-4 py-2 rounded-full glass-card border border-white/5 text-[11px] font-black text-zinc-400 hover:text-white hover:border-cyan-500/30 transition-all uppercase tracking-tight">
                                                    {ex}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                )}
                                <AnimatePresence>
                                    {messages.map((m, i) => (
                                        <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                                            <div className={`max-w-[85%] px-5 py-3 rounded-2xl text-sm font-bold shadow-2xl ${m.role === "user" ? "bg-cyan-500/10 border border-cyan-500/20 text-cyan-100" : "bg-zinc-900 border border-white/5 text-zinc-300"}`}>
                                                {m.content}
                                            </div>
                                        </motion.div>
                                    ))}
                                </AnimatePresence>
                                {loading && (
                                    <div className="flex justify-start">
                                        <div className="px-5 py-3 rounded-2xl bg-zinc-900 border border-white/5 flex gap-1.5 items-center">
                                            {[0, 1, 2].map((i) => (
                                                <motion.div key={i} animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1, delay: i * 0.2 }} className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                                            ))}
                                        </div>
                                    </div>
                                )}
                                <div ref={chatEnd} />
                            </div>

                            {/* Input */}
                            <div className="shrink-0 border-t border-white/5 p-6 glass">
                                <div className="flex gap-4 max-w-4xl mx-auto">
                                    <input
                                        value={input}
                                        onChange={(e) => setInput(e.target.value)}
                                        onKeyDown={(e) => e.key === "Enter" && handleSend()}
                                        placeholder={activeTab === "single" ? "Message the default agent..." : `Messaging as ${selectedAgent}...`}
                                        className="flex-1 h-14 px-6 bg-zinc-900/50 border border-white/5 rounded-2xl text-sm font-bold text-white placeholder:text-zinc-600 focus:outline-none focus:border-cyan-500/30 transition-all"
                                    />
                                    <Button onClick={handleSend} disabled={loading || !input.trim() || (activeTab === 'multi' && !selectedAgent)} className="h-14 w-14 bg-cyan-500 hover:bg-cyan-400 text-black rounded-2xl p-0 flex items-center justify-center group shrink-0 shadow-lg shadow-cyan-500/10">
                                        <Send className="w-5 h-5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                                    </Button>
                                </div>
                            </div>
                        </>
                    )}
                </div>

                {/* Right Panel */}
                <div className="w-[420px] border-l border-white/5 flex flex-col shrink-0 hidden xl:flex bg-zinc-950">
                    {/* Tabs */}
                    <div className="shrink-0 flex border-b border-white/5 bg-zinc-900/10">
                        {[
                            { key: "logs" as const, icon: Terminal, label: "System Traces" },
                            { key: "timeline" as const, icon: Clock, label: "Timeline" },
                            { key: "insights" as const, icon: Lightbulb, label: "Insights" },
                            { key: "recall" as const, icon: Search, label: "Recall Pool" },
                            ...(activeTab === "ame" ? [{ key: "schemas" as const, icon: Layers, label: "Schemas" }] : [])
                        ].map((t) => (
                            <button key={t.key} onClick={() => setRightTab(t.key)} className={`flex-1 py-4 flex flex-col items-center justify-center gap-1.5 text-[9px] font-black uppercase tracking-widest transition-all ${rightTab === t.key ? "text-cyan-400 border-b-2 border-cyan-400 bg-cyan-500/5" : "text-zinc-600 hover:text-zinc-400 hover:bg-white/5"}`}>
                                <t.icon className="w-3.5 h-3.5" /> <span>{t.label}</span>
                            </button>
                        ))}
                    </div>

                    <div className="flex-1 overflow-y-auto p-5 space-y-3 custom-scrollbar">
                        {rightTab === "logs" && (
                            processingLogs.length > 0 ? (
                                <>
                                    <div className="flex items-center justify-between mb-4">
                                        <span className="text-[10px] font-black uppercase tracking-widest text-zinc-500">Pipeline Execution</span>
                                        <Badge className="bg-zinc-900 border-white/5 text-zinc-500 text-[9px] px-1.5">{processingLogs.length} nodes</Badge>
                                    </div>
                                    <div className="space-y-2">
                                        {processingLogs.map((log, i) => {
                                            const sys = systemColors[log.system] || systemColors.python;
                                            return (
                                                <motion.div key={i} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }} className="rounded-xl bg-zinc-900/40 border border-white/5 overflow-hidden">
                                                    <div className="flex items-center gap-2 px-3 py-2 bg-white/5 border-b border-white/5">
                                                        <span className={`text-[7px] font-black px-1.5 py-0.5 rounded border ${sys.text} ${sys.border} ${sys.bg}`}>{sys.label}</span>
                                                        <span className="text-[10px] font-black text-white flex-1 truncate">{log.stage}</span>
                                                        <span className="text-[9px] font-bold text-zinc-600">{log.duration_ms}ms</span>
                                                    </div>
                                                    <div className="px-3 py-2">
                                                        <p className="text-[11px] font-bold text-zinc-500 leading-relaxed">{log.detail}</p>
                                                    </div>
                                                </motion.div>
                                            );
                                        })}
                                    </div>
                                </>
                            ) : (
                                <div className="text-center py-20 px-10">
                                    <div className="w-12 h-12 rounded-2xl bg-zinc-900 flex items-center justify-center mx-auto mb-6 border border-white/5">
                                        <Terminal className="w-6 h-6 text-zinc-700" />
                                    </div>
                                    <h4 className="text-sm font-black text-zinc-500 uppercase mb-2">Cognitive Trace</h4>
                                    <p className="text-xs font-bold text-zinc-700 leading-relaxed">Send a memory to witness the multi-layer storage pipeline in real-time.</p>
                                </div>
                            )
                        )}

                        {rightTab === "timeline" && (
                            timeline.length > 0 ? timeline.map((e, i) => (
                                <motion.div key={i} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="p-4 rounded-2xl bg-zinc-900/40 border border-white/5 relative overflow-hidden group">
                                    <div className="absolute top-0 left-0 w-1 h-full bg-cyan-500/20 group-hover:bg-cyan-500 transition-colors" />
                                    <p className="text-xs font-bold text-zinc-300 leading-relaxed">{e.content}</p>
                                    <div className="flex items-center gap-2 mt-3">
                                        <Clock className="w-3 h-3 text-zinc-600" />
                                        <span className="text-[10px] font-black text-zinc-600 uppercase tracking-tighter">{new Date(e.timestamp * 1000).toLocaleTimeString()}</span>
                                    </div>
                                </motion.div>
                            )) : <div className="text-center py-20 text-zinc-700 font-black uppercase text-[10px]">Empty Chronology</div>
                        )}

                        {rightTab === "insights" && (
                            insights.length > 0 ? insights.map((ins, i) => (
                                <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="p-4 rounded-2xl bg-purple-500/5 border border-purple-500/10 hover:bg-purple-500/10 transition-colors">
                                    <div className="flex items-center gap-2 mb-2">
                                        <Lightbulb className="w-3.5 h-3.5 text-purple-400" />
                                        <span className="text-[9px] font-black text-purple-400 uppercase tracking-widest">Behavioral Pattern</span>
                                    </div>
                                    <p className="text-xs font-bold text-zinc-300 leading-relaxed underline-offset-4 decoration-purple-500/30 underline decoration-2">{ins.summary}</p>
                                    <div className="flex items-center justify-between mt-4">
                                        <div className="flex items-center gap-2">
                                            <div className="h-1 w-12 bg-zinc-800 rounded-full overflow-hidden">
                                                <motion.div initial={{ width: 0 }} animate={{ width: `${ins.confidence * 100}%` }} className="h-full bg-purple-500" />
                                            </div>
                                            <span className="text-[9px] font-black text-zinc-600">{Math.round(ins.confidence * 100)}%</span>
                                        </div>
                                        <span className="text-[9px] text-zinc-700 font-bold uppercase">{new Date(ins.timestamp * 1000).toLocaleDateString()}</span>
                                    </div>
                                </motion.div>
                            )) : <div className="text-center py-20 text-zinc-700 font-black uppercase text-[10px]">No Neural Insights</div>
                        )}

                        {rightTab === "recall" && (
                            <div className="space-y-4">
                                {recallResults.intent && (
                                    <div className="p-4 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 mb-4 transition-all">
                                        <div className="flex items-center justify-between mb-3">
                                            <div className="flex items-center gap-2">
                                                <Target className="w-3.5 h-3.5 text-cyan-400" />
                                                <span className="text-[10px] font-black text-cyan-400 uppercase tracking-widest">Inferred Intent</span>
                                            </div>
                                            <Badge className="bg-cyan-500/20 text-cyan-400 border-none text-[9px] px-1.5 font-black">{(recallResults.confidence * 100).toFixed(0)}% CONFIDENCE</Badge>
                                        </div>
                                        <h4 className="text-xl font-black text-white uppercase mb-1">{recallResults.intent}</h4>
                                        <p className="text-[10px] font-bold text-zinc-500">Domain: {recallResults.context_inference?.domain || 'General'}</p>
                                        
                                        {recallResults.retrieval_plan?.memory_types && (
                                            <div className="mt-4 pt-4 border-t border-white/5">
                                                <span className="text-[9px] font-black text-zinc-600 uppercase tracking-tighter block mb-2">Automated Retrieval Plan</span>
                                                <div className="flex flex-wrap gap-1.5">
                                                    {recallResults.retrieval_plan.memory_types.map((t: string) => (
                                                        <Badge key={t} variant="outline" className="text-[8px] border-cyan-500/30 text-cyan-500 bg-cyan-500/5 px-1.5 py-0 uppercase">{t}</Badge>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}

                                {(recallResults.memories || recallResults.final_memories || []).length > 0 ? (recallResults.memories || recallResults.final_memories || []).map((r: any, i: number) => (
                                    <motion.div key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="p-4 rounded-2xl bg-zinc-900 border border-white/5 hover:border-cyan-500/30 transition-all group">
                                        <div className="flex items-center justify-between mb-2">
                                            <Badge className="text-[8px] bg-cyan-500/10 text-cyan-400 border-cyan-500/20 px-1 font-black">{r.source || r.type || 'SEMANTIC'}</Badge>
                                            <span className="text-[10px] font-black text-zinc-600">{i + 1}</span>
                                        </div>
                                        <p className="text-xs font-bold text-zinc-300 leading-relaxed group-hover:text-white transition-colors">{r.content || JSON.stringify(r)}</p>
                                        {(r.importance || r.relevance) && (
                                            <div className="mt-3 pt-3 border-t border-white/5 flex items-center justify-between">
                                                <span className="text-[9px] font-black text-zinc-600 uppercase">Attention Weight</span>
                                                <span className="text-[10px] font-black text-cyan-500">{(r.importance || r.relevance).toFixed(2)}</span>
                                            </div>
                                        )}
                                    </motion.div>
                                )) : <div className="text-center py-20 text-zinc-700 font-black uppercase text-[10px]">No Semantic Matches</div>}
                            </div>
                        )}

                        {rightTab === "schemas" && (
                            <div className="space-y-4">
                                {schemas.map((s, i) => (
                                    <div key={i} className="p-4 rounded-2xl bg-emerald-500/5 border border-emerald-500/10">
                                        <div className="flex items-center gap-2 mb-2">
                                            <Database className="w-3.5 h-3.5 text-emerald-400" />
                                            <span className="text-[9px] font-black text-emerald-400 uppercase tracking-widest">Active Concept</span>
                                        </div>
                                        <h5 className="text-xs font-black text-white uppercase mb-2">{s.schema_id}</h5>
                                        <div className="flex flex-wrap gap-1.5">
                                            {s.fields?.map((f: string) => (
                                                <span key={f} className="text-[8px] font-black px-1.5 py-0.5 rounded-md bg-zinc-900 border border-white/5 text-zinc-500">{f}</span>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
