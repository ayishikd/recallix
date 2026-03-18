"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
    Activity, Zap, Database, Search, RefreshCw,
    Cpu, ArrowUpRight, ArrowLeft, Brain, Sparkles
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
    AreaChart, Area, XAxis, YAxis, CartesianGrid,
    Tooltip, ResponsiveContainer
} from "recharts";
import { memoryApi } from "@/lib/api";
import Link from "next/link";

const chartData = [
    { time: "10:00", queries: 40, memories: 240 },
    { time: "11:00", queries: 30, memories: 330 },
    { time: "12:00", queries: 60, memories: 420 },
    { time: "13:00", queries: 45, memories: 510 },
    { time: "14:00", queries: 90, memories: 600 },
    { time: "15:00", queries: 75, memories: 750 },
    { time: "16:00", queries: 120, memories: 840 },
];

const MetricCard = ({ title, value, unit, icon: Icon, trend, loading }: any) => (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-6 rounded-[24px] border-white/5 relative group overflow-hidden">
        <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/5 blur-3xl group-hover:bg-cyan-500/10 transition-colors" />
        <div className="flex justify-between items-start mb-4">
            <div className="p-2.5 rounded-xl bg-white/5 border border-white/10"><Icon className="w-4 h-4 text-white" /></div>
            {trend && (
                <Badge className="bg-green-500/10 text-green-400 border-green-500/20 text-[9px] font-black">
                    <ArrowUpRight className="w-2.5 h-2.5 mr-0.5" />{trend}
                </Badge>
            )}
        </div>
        <div className="text-[10px] font-black uppercase tracking-widest text-zinc-500 mb-1">{title}</div>
        <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-white tracking-tighter">{loading ? "—" : value}</span>
            <span className="text-xs font-bold text-zinc-600 uppercase">{unit}</span>
        </div>
    </motion.div>
);

export default function ObservabilityPage() {
    const [isClient, setIsClient] = useState(false);
    const [stats, setStats] = useState<any>(null);
    const [metaInsights, setMetaInsights] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setIsClient(true);
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        const [statsRes, metaRes] = await Promise.all([
            memoryApi.stats(),
            memoryApi.metaInsights(),
        ]);
        if (statsRes.data) setStats(statsRes.data);
        if (metaRes.data) setMetaInsights(Array.isArray(metaRes.data) ? metaRes.data : []);
        setLoading(false);
    };

    const clusters = [
        { label: "High Level Reasoning", usage: 84, color: "bg-cyan-500" },
        { label: "Episodic Recall", usage: 62, color: "bg-purple-500" },
        { label: "Semantic Linking", usage: 45, color: "bg-zinc-500" },
        { label: "Meta Optimization", usage: 28, color: "bg-blue-500" },
    ];

    return (
        <div className="min-h-screen bg-black text-white selection:bg-cyan-500/30">
            <nav className="fixed top-0 left-0 right-0 z-50 h-14 border-b border-white/5 flex items-center justify-between px-6 glass backdrop-blur-2xl">
                <div className="flex items-center gap-4">
                    <Link href="/" className="flex items-center gap-2 text-zinc-400 hover:text-white transition-colors">
                        <ArrowLeft className="w-4 h-4" /> <Activity className="w-5 h-5 text-cyan-400" />
                    </Link>
                    <span className="text-sm font-black tracking-tight">OBSERVABILITY HUB</span>
                </div>
                <div className="flex items-center gap-3">
                    <span className="text-[10px] font-black uppercase tracking-widest text-green-400 flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" /> Live
                    </span>
                    <Button variant="ghost" size="sm" onClick={loadData} className="text-zinc-500 hover:text-white">
                        <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
                    </Button>
                    <Link href="/playground"><Button variant="outline" size="sm" className="h-8 border-white/10 rounded-full text-xs font-bold">Playground</Button></Link>
                </div>
            </nav>

            <main className="pt-24 pb-24 container mx-auto px-6">
                {/* Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
                    <MetricCard title="Stored Memories" value={stats?.episodic_memories ?? 0} unit="events" icon={Database} trend="+12%" loading={loading} />
                    <MetricCard title="Timeline Events" value={stats?.timeline_events ?? 0} unit="nodes" icon={Zap} loading={loading} />
                    <MetricCard title="Reflections" value={stats?.reflections ?? 0} unit="insights" icon={RefreshCw} loading={loading} />
                    <MetricCard title="Active Schemas" value={stats?.evolved_schemas ?? 0} unit="AME" icon={Sparkles} loading={loading} />
                    <MetricCard title="Active Agents" value={stats?.active_agents ?? 0} unit="registered" icon={Brain} loading={loading} />
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                    {/* Chart */}
                    <div className="lg:col-span-2 glass-card rounded-[28px] border-white/5 p-6 flex flex-col h-[360px]">
                        <div className="flex justify-between items-center mb-6">
                            <div>
                                <h3 className="text-lg font-black tracking-tight">System Utilization</h3>
                                <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Memory growth vs Query volume</p>
                            </div>
                            <div className="flex gap-4">
                                <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-cyan-500" /><span className="text-[10px] font-black uppercase text-zinc-500">Memories</span></div>
                                <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-purple-500" /><span className="text-[10px] font-black uppercase text-zinc-500">Queries</span></div>
                            </div>
                        </div>
                        <div className="flex-1 w-full">
                            {isClient && (
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={chartData}>
                                        <defs>
                                            <linearGradient id="colorMem" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.1} />
                                                <stop offset="95%" stopColor="#22d3ee" stopOpacity={0} />
                                            </linearGradient>
                                            <linearGradient id="colorQue" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#a78bfa" stopOpacity={0.1} />
                                                <stop offset="95%" stopColor="#a78bfa" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1f2937" />
                                        <XAxis dataKey="time" stroke="#6b7280" fontSize={10} axisLine={false} tickLine={false} />
                                        <YAxis stroke="#6b7280" fontSize={10} axisLine={false} tickLine={false} />
                                        <Tooltip contentStyle={{ backgroundColor: "#09090b", border: "1px solid #1f2937", borderRadius: "12px" }} itemStyle={{ color: "#fff" }} />
                                        <Area type="monotone" dataKey="memories" stroke="#22d3ee" strokeWidth={2} fillOpacity={1} fill="url(#colorMem)" />
                                        <Area type="monotone" dataKey="queries" stroke="#a78bfa" strokeWidth={2} fillOpacity={1} fill="url(#colorQue)" />
                                    </AreaChart>
                                </ResponsiveContainer>
                            )}
                        </div>
                    </div>

                    {/* Cluster Analysis */}
                    <div className="glass-card rounded-[28px] border-white/5 p-6 flex flex-col">
                        <h3 className="text-lg font-black tracking-tight mb-6">Cluster Analysis</h3>
                        <div className="space-y-6 flex-1">
                            {clusters.map((c, i) => (
                                <div key={i} className="space-y-2">
                                    <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest">
                                        <span className="text-zinc-500">{c.label}</span>
                                        <span className="text-white">{c.usage}%</span>
                                    </div>
                                    <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                                        <motion.div initial={{ width: 0 }} animate={{ width: `${c.usage}%` }} transition={{ duration: 1, delay: i * 0.1 }} className={`h-full ${c.color}`} />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Meta-Memory Insights (live from backend) */}
                <div className="glass-card rounded-[28px] border-white/5 p-6 mb-8">
                    <div className="flex items-center gap-3 mb-6">
                        <Sparkles className="w-5 h-5 text-purple-400" />
                        <h3 className="text-lg font-black tracking-tight">Meta-Memory Insights</h3>
                        <Badge className="text-[9px] bg-purple-500/10 border-purple-500/20 text-purple-400 font-black">LIVE FROM BACKEND</Badge>
                    </div>
                    {metaInsights.length > 0 ? (
                        <div className="space-y-3">
                            {metaInsights.map((ins, i) => (
                                <div key={i} className="p-3 rounded-xl bg-zinc-900/50 border border-zinc-800/50 flex items-start gap-3">
                                    <Badge className="text-[9px] bg-zinc-800 text-zinc-400 border-zinc-700 shrink-0 mt-0.5">{ins.meta_type}</Badge>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-xs font-bold text-zinc-300 leading-relaxed">{ins.insight_text}</p>
                                        <p className="text-[10px] text-zinc-600 mt-1">Component: {ins.component} · Confidence: {Math.round(ins.confidence * 100)}%</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-xs font-bold text-zinc-600 text-center py-8">No meta-memory insights yet. Run the meta-memory worker to generate insights.</p>
                    )}
                </div>

                {/* Infrastructure */}
                <div className="bg-zinc-900/40 rounded-[28px] border border-white/5 p-6 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-full bg-white/5 border border-white/10 flex items-center justify-center">
                            <Cpu className="w-6 h-6 text-zinc-500" />
                        </div>
                        <div>
                            <h4 className="text-sm font-black tracking-tight">Local Infrastructure Detected</h4>
                            <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">macOS Darwin · Ollama Active · C++ Infra on :8080</p>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
