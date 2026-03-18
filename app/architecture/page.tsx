"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Brain, Cpu, Database, GitBranch, Layers,
    ArrowLeft, ChevronRight, Sparkles, Clock,
    Search, Shield, RefreshCw, Lightbulb
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";

interface Component {
    id: string;
    title: string;
    desc: string;
    icon: any;
    color: string;
    modules: { name: string; detail: string }[];
}

const components: Component[] = [
    {
        id: "brain",
        title: "Python AI Brain",
        desc: "Orchestrates all cognitive processes. Routes between local models (Mistral, Llama 3.1) via Ollama.",
        icon: Brain,
        color: "cyan",
        modules: [
            { name: "MemoryManager", detail: "Central orchestrator: 12-step store pipeline, multi-layer retrieve" },
            { name: "RecallEngine", detail: "Two-stage retrieval: Intent-Driven routing → fast vector search (50 candidates) → neural reranking (top 20) → attention filter (top 5)" },
            { name: "IntentDetector", detail: "Classifies query into 6 cognitive intents (learning, preference, research, etc.) with sub-10ms latency" },
            { name: "RetrievalPlanner", detail: "Translates intent + context into dynamic multi-engine search plans" },
            { name: "MemoryRouter", detail: "Routes requests between isolated agent pools and shared cognitive layers" },
            { name: "ContextInference", detail: "Infers topic, domain, and user state from raw query to guide retrieval" },
            { name: "ImportanceRanker", detail: "Keyword-based cognitive scoring: goal +3, preference +2, explicit +4, noise -3" },
        ],
    },
    {
        id: "cpp",
        title: "C++ Infrastructure",
        desc: "High-performance engines for vector operations, graph traversal, and timeline management. Runs on port 8080.",
        icon: Cpu,
        color: "purple",
        modules: [
            { name: "VectorEngine", detail: "Brute-force cosine similarity with binary file persistence (128D vectors)" },
            { name: "GraphEngine", detail: "In-memory adjacency list for entity-relationship knowledge graph" },
            { name: "TimelineEngine", detail: "Chronological event storage with pattern detection support" },
            { name: "ClusteringEngine", detail: "Topic-based memory grouping for semantic organization" },
            { name: "MemoryIndexer", detail: "Importance + access count tracking with compaction for cleanup" },
            { name: "EventQueue", detail: "FIFO buffer for inter-process communication" },
        ],
    },
    {
        id: "memory",
        title: "6-Layer Memory Architecture",
        desc: "Human-inspired cognitive memory hierarchy from 60s sensory buffer to self-evolving meta-memory.",
        icon: Layers,
        color: "emerald",
        modules: [
            { name: "Sensory Memory", detail: "In-memory deque with 60s TTL, max 10 items per user — captures raw input" },
            { name: "Working Memory", detail: "JSON-based active session context, append-only summary of conversation" },
            { name: "Episodic Memory", detail: "SQLite (WAL mode) with keyword search, access tracking, reinforcement scores" },
            { name: "Semantic Memory", detail: "128D embeddings → C++ vector engine via HTTP for cosine similarity search" },
            { name: "Long-Term Memory", detail: "Importance-gated promotion (score > 8), Ebbinghaus decay-based retention" },
            { name: "Reflective Memory", detail: "LLM-generated behavioral insights with confidence scores" },
        ],
    },
    {
        id: "world",
        title: "World Model & Meta-Memory",
        desc: "Predictive intelligence and self-optimization. The system learns to improve its own memory management.",
        icon: Sparkles,
        color: "amber",
        modules: [
            { name: "StateInference", detail: "LLM infers hidden user states (skill_level, interest_strength) → SQLite" },
            { name: "PredictionEngine", detail: "Predicts future user needs via LLM, caches results for preloading" },
            { name: "PlanningEngine", detail: "Generates proactive multi-step cognitive plans from predictions" },
            { name: "MetaAnalyzer", detail: "Detects recurring themes via keyword frequency across timeline + reflections" },
            { name: "SchemaOptimizer", detail: "Auto-creates categories in schema_registry.json when patterns emerge" },
            { name: "PolicyOptimizer", detail: "Adjusts attention weights and forgetting thresholds based on recall metrics" },
        ],
    },
    {
        id: "workers",
        title: "Background Workers",
        desc: "10 daemon threads maintain system health: reflection, clustering, decay, compression, replay, ranking, forgetting, and meta-analysis.",
        icon: RefreshCw,
        color: "rose",
        modules: [
            { name: "ReflectionWorker", detail: "Every 1h: triggers LLM-based insight generation from recent memories" },
            { name: "CompressionWorker", detail: "Every 30m: hierarchical conversation → topic summarization" },
            { name: "ReplayWorker", detail: "Every 6h: sleep-cycle consolidation from Long-Term → Reflective" },
            { name: "RankingWorker", detail: "Every 1h: importance decay (30-day half-life) + auto-promotion to LT" },
            { name: "ForgettingWorker", detail: "Every 24h: RL-based delete/archive/protect with atomic multi-store deletion" },
            { name: "MetaMemoryWorker", detail: "Every 12h: pattern detection → schema evolution → policy optimization" },
        ],
    },
    {
        id: "multi-agent",
        title: "Multi-Agent System",
        desc: "Scalable infrastructure for parallel AI orchestration and shared cognitive boundaries.",
        icon: Shield,
        color: "cyan",
        modules: [
            { name: "AgentRegistry", detail: "Central authority for agent identities, roles, and context boundaries" },
            { name: "PrivacyEngine", detail: "Enforces strict access control: private (agent-only) vs shared (broadcast)" },
            { name: "CoordinationLayer", detail: "Synchronizes shared memory state and cross-agent event triggers" },
            { name: "AgentRouter", detail: "Routes recall requests based on agent_id to isolated cognitive pools" },
        ],
    },
    {
        id: "ame",
        title: "AME Evolution Engine",
        desc: "Autonomous Memory Evolution: self-organizing schemas that adapt to user behavioral patterns.",
        icon: GitBranch,
        color: "emerald",
        modules: [
            { name: "ConceptDetector", detail: "Clustering-based pattern matching across episodic memory timeline" },
            { name: "SchemaProposer", detail: "LLM-driven schema generation for high-confidence conceptual clusters" },
            { name: "MemoryMigrator", detail: "Background migration of unstructured logs into evolved structured schemas" },
            { name: "SchemaRegistry", detail: "Dynamic persistence of discovered conceptual frameworks" },
        ],
    },
];

const colorBg: Record<string, string> = {
    cyan: "bg-cyan-500/10 border-cyan-500/20 text-cyan-400",
    purple: "bg-purple-500/10 border-purple-500/20 text-purple-400",
    emerald: "bg-emerald-500/10 border-emerald-500/20 text-emerald-400",
    amber: "bg-amber-500/10 border-amber-500/20 text-amber-400",
    rose: "bg-rose-500/10 border-rose-500/20 text-rose-400",
};

export default function ArchitecturePage() {
    const [selected, setSelected] = useState<string | null>(null);
    const activeComponent = components.find((c) => c.id === selected);

    return (
        <div className="min-h-screen bg-black text-white selection:bg-cyan-500/30">
            <nav className="fixed top-0 left-0 right-0 z-50 h-14 border-b border-white/5 flex items-center justify-between px-6 glass backdrop-blur-2xl">
                <div className="flex items-center gap-4">
                    <Link href="/" className="flex items-center gap-2 text-zinc-400 hover:text-white transition-colors">
                        <ArrowLeft className="w-4 h-4" /> <Brain className="w-5 h-5 text-cyan-400" />
                    </Link>
                    <span className="text-sm font-black tracking-tight">ARCHITECTURE</span>
                </div>
                <Link href="/playground"><Button variant="outline" size="sm" className="h-8 border-white/10 rounded-full text-xs font-bold">Playground</Button></Link>
            </nav>

            <main className="pt-28 pb-24 container mx-auto px-6 max-w-6xl">
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-16">
                    <h1 className="text-5xl md:text-6xl font-black tracking-tighter mb-4">
                        System Architecture
                    </h1>
                    <p className="text-lg text-zinc-500 font-bold max-w-2xl mx-auto">
                        Click any component to explore its internal modules and design decisions.
                    </p>
                </motion.div>

                {/* Component Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-12">
                    {components.map((comp, i) => {
                        const colors = colorBg[comp.color];
                        const isActive = selected === comp.id;
                        return (
                            <motion.button
                                key={comp.id}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: i * 0.05 }}
                                onClick={() => setSelected(isActive ? null : comp.id)}
                                className={`text-left p-6 rounded-[24px] border transition-all duration-300 ${isActive
                                    ? "bg-zinc-900 border-cyan-500/30 ring-1 ring-cyan-500/20"
                                    : "glass-card border-white/5 hover:border-white/10"
                                    }`}
                            >
                                <div className="flex items-start justify-between mb-4">
                                    <div className={`w-11 h-11 rounded-xl border flex items-center justify-center ${colors}`}>
                                        <comp.icon className="w-5 h-5" />
                                    </div>
                                    <ChevronRight className={`w-4 h-4 text-zinc-600 transition-transform ${isActive ? "rotate-90" : ""}`} />
                                </div>
                                <h3 className="text-base font-black tracking-tight mb-1">{comp.title}</h3>
                                <p className="text-xs text-zinc-500 font-bold leading-relaxed">{comp.desc}</p>
                            </motion.button>
                        );
                    })}
                </div>

                {/* Detail Panel */}
                <AnimatePresence mode="wait">
                    {activeComponent && (
                        <motion.div
                            key={activeComponent.id}
                            initial={{ opacity: 0, y: 20, height: 0 }}
                            animate={{ opacity: 1, y: 0, height: "auto" }}
                            exit={{ opacity: 0, y: -10, height: 0 }}
                            transition={{ duration: 0.3 }}
                            className="overflow-hidden"
                        >
                            <div className="bg-zinc-900/50 rounded-[32px] border border-white/5 p-8 md:p-10">
                                <div className="flex items-center gap-3 mb-8">
                                    <div className={`w-10 h-10 rounded-xl border flex items-center justify-center ${colorBg[activeComponent.color]}`}>
                                        <activeComponent.icon className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <h2 className="text-xl font-black tracking-tight">{activeComponent.title}</h2>
                                        <p className="text-xs text-zinc-500 font-bold">{activeComponent.modules.length} modules</p>
                                    </div>
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {activeComponent.modules.map((mod, i) => (
                                        <motion.div
                                            key={mod.name}
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: i * 0.04 }}
                                            className="p-4 rounded-xl bg-zinc-950/50 border border-zinc-800/50 hover:border-zinc-700 transition-colors"
                                        >
                                            <h4 className="text-sm font-black text-white mb-1.5">{mod.name}</h4>
                                            <p className="text-xs text-zinc-500 font-bold leading-relaxed">{mod.detail}</p>
                                        </motion.div>
                                    ))}
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Data Flow */}
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="mt-16">
                    <h2 className="text-2xl font-black tracking-tighter mb-8 text-center">Data Flow</h2>
                    <div className="glass-card rounded-[28px] p-8 max-w-3xl mx-auto">
                        <div className="space-y-4">
                            {[
                                { from: "User Message", to: "Python API (FastAPI, :8000)", color: "text-white" },
                                { from: "Intent Detection", to: "Classifier + Context Inference", color: "text-cyan-400" },
                                { from: "Retrieval Planning", to: "Multi-Engine Search Plan", color: "text-blue-400" },
                                { from: "MemoryManager.store()", to: "12-Step Pipeline", color: "text-cyan-400" },
                                { from: "Sensory → Working → Episodic", to: "SQLite (WAL Mode)", color: "text-emerald-400" },
                                { from: "Semantic Embedding", to: "C++ VectorEngine (:8080)", color: "text-purple-400" },
                                { from: "Importance > 8", to: "Promoted to Long-Term", color: "text-amber-400" },
                                { from: "Timeline Updated", to: "C++ TimelineEngine", color: "text-blue-400" },
                                { from: "State Inference", to: "World Model SQLite", color: "text-rose-400" },
                                { from: "Background Workers", to: "Reflection → Meta-Memory → Schema Evolution", color: "text-cyan-400" },
                            ].map((flow, i) => (
                                <div key={i} className="flex items-center gap-3">
                                    <div className="text-[10px] font-black text-zinc-500 w-6 text-right">{i + 1}</div>
                                    <div className="flex-1 flex items-center gap-2">
                                        <span className={`text-xs font-black ${flow.color}`}>{flow.from}</span>
                                        <div className="flex-1 h-px bg-zinc-800" />
                                        <span className="text-xs font-bold text-zinc-500">{flow.to}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </motion.div>
            </main>
        </div>
    );
}
