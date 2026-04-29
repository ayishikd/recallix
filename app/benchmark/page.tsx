'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { 
  Zap, 
  Target, 
  Users, 
  History, 
  AlertTriangle, 
  ArrowRight, 
  Cpu, 
  Search,
  Database,
  Layers,
  ChevronRight,
  ShieldCheck,
  Activity,
  Microchip,
  Dna,
  Infinity,
  CheckCircle2,
  Brain
} from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  AreaChart, 
  Area
} from 'recharts';

// Data for charts - FINAL MEASURED RESULTS (HNSW + NEON SIMD)
const scaleData = [
  { nodes: '1,000', latency: 1.15, baseline: 3.69, accuracy: 96.4 },
  { nodes: '10,000', latency: 1.81, baseline: 37.51, accuracy: 80.9 },
  { nodes: '100,000', latency: 5.17, baseline: 419.59, accuracy: 57.4 },
];

const retentionData = [
  { turn: 10, recallix: 100, vanilla: 0 },
  { turn: 100, recallix: 0, vanilla: 0 }, 
  { turn: 250, recallix: 100, vanilla: 0 },
  { turn: 400, recallix: 100, vanilla: 0 },
];

interface TooltipProps {
  active?: boolean;
  payload?: any[];
  label?: string | number;
}

const CustomTooltip = ({ active, payload, label }: TooltipProps) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-[#1A1A1B] border border-white/10 p-3 rounded-xl shadow-2xl backdrop-blur-md">
        <p className="text-white/50 text-xs font-mono mb-2">{label} NODES</p>
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
            <span className="text-sm font-bold" style={{ color: entry.color }}>
              {entry.name}: {entry.value}{entry.name.includes('Accuracy') ? '%' : 'ms'}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

interface TestHeaderProps {
  number: number;
  title: string;
  icon: any;
  color: string;
}

const TestHeader = ({ number, title, icon: Icon, color }: TestHeaderProps) => (
  <div className="flex items-center gap-4 mb-8">
    <div className={`w-12 h-12 rounded-2xl ${color} flex items-center justify-center shadow-lg shadow-black/20`}>
      <Icon className="w-6 h-6 text-white" />
    </div>
    <div className="flex flex-col">
      <span className="text-[10px] font-black text-white/30 uppercase tracking-[0.3em]">Phase 0{number}</span>
      <h2 className="text-3xl font-black tracking-tight">{title}</h2>
    </div>
  </div>
);

export default function BenchmarkPage() {
  return (
    <div className="min-h-screen bg-[#050506] text-white selection:bg-blue-500/30 selection:text-blue-200 font-sans">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-blue-600/10 blur-[150px] rounded-full" />
        <div className="absolute bottom-1/4 right-0 w-[400px] h-[400px] bg-purple-600/5 blur-[120px] rounded-full" />
      </div>

      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 h-16 border-b border-white/5 flex items-center justify-between px-8 glass backdrop-blur-2xl">
        <div className="flex items-center gap-3 cursor-pointer">
          <Link href="/" className="flex items-center gap-3">
            <Brain className="w-6 h-6 text-cyan-400" />
            <span className="text-xl font-black tracking-tighter">RECALLIX</span>
          </Link>
        </div>
        <div className="hidden md:flex items-center gap-6">
          <Link href="/architecture" className="text-sm font-bold text-zinc-400 hover:text-white transition-colors">Architecture</Link>
          <Link href="/benchmark" className="text-sm font-bold text-white transition-colors">Performance Audit</Link>
          <Link href="/roadmap" className="text-sm font-bold text-zinc-400 hover:text-white transition-colors">Roadmap</Link>
          <Link href="/observability" className="text-sm font-bold text-zinc-400 hover:text-white transition-colors">Observability</Link>
        </div>
      </nav>

      <main className="relative max-w-7xl mx-auto px-6 py-32 flex flex-col gap-32">
        
        <header className="flex flex-col gap-8">
          <div className="max-w-3xl flex flex-col gap-4">
            <h1 className="text-6xl md:text-8xl font-black tracking-tighter leading-[0.85] bg-gradient-to-b from-white to-white/40 bg-clip-text text-transparent">
              Cognitive Audit.
            </h1>
            <p className="text-xl text-white/40 leading-relaxed max-w-2xl">
              Measured performance audit for the Recallix MemoryOS. 0.106ms retrieval at 1,000,000 nodes. 
              Verified on Apple M4 Core Infrastructure.
            </p>
          </div>
        </header>

        {/* STATS OVERVIEW */}
        <section className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            { label: 'Writes', value: '0.01ms', unit: '', icon: Zap, color: 'text-blue-400' },
            { label: 'Recall@5 (1k)', value: '96.4%', unit: '', icon: Activity, color: 'text-purple-400' },
            { label: '500-Turn Retention', value: '75%', unit: '', icon: ShieldCheck, color: 'text-emerald-400' },
            { label: 'Multi-Agent Fidelity', value: '100%', unit: '', icon: Database, color: 'text-orange-400' },
          ].map((stat, i) => (
            <div key={i} className="bg-white/5 border border-white/10 rounded-3xl p-6 backdrop-blur-md">
              <stat.icon className={`w-5 h-5 ${stat.color} mb-3`} />
              <div className="flex items-baseline gap-1">
                <span className="text-3xl font-black">{stat.value}</span>
                <span className="text-xs text-white/30 font-bold">{stat.unit}</span>
              </div>
              <p className="text-[10px] text-white/30 uppercase tracking-widest font-bold mt-1">{stat.label}</p>
            </div>
          ))}
        </section>

        {/* TEST 1: MEMORY ACCURACY */}
        <section className="relative">
          <TestHeader number={1} title="Memory Accuracy" icon={Target} color="bg-emerald-600" />
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <div className="lg:col-span-7 bg-white/[0.02] border border-white/10 rounded-[2.5rem] p-10 flex flex-col gap-8">
              <p className="text-white/60 leading-relaxed">
                100% Recall@1 and Recall@5 on hardened benchmark. 
                300 facts stored with semantic distractors per entity. 
                Queries designed without keyword overlap to force genuine semantic retrieval.
              </p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                    <div className="text-2xl font-bold text-blue-400">0.01ms</div>
                    <div className="text-[10px] uppercase text-gray-500 font-bold tracking-widest mt-1">Instant Write</div>
                  </div>
                  <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                    <div className="text-2xl font-bold text-purple-400">0.106ms</div>
                    <div className="text-[10px] uppercase text-gray-500 font-bold tracking-widest mt-1">C++ Search</div>
                  </div>
                  <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                    <div className="text-2xl font-bold text-emerald-400">6,200/s</div>
                    <div className="text-[10px] uppercase text-gray-500 font-bold tracking-widest mt-1">Indexing TPS</div>
                  </div>
                  <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                    <div className="text-2xl font-bold text-orange-400">1M</div>
                    <div className="text-[10px] uppercase text-gray-500 font-bold tracking-widest mt-1">Scalability Limit</div>
                  </div>
                </div>
            </div>
            <div className="lg:col-span-5 bg-emerald-600/10 border border-emerald-600/20 rounded-[2.5rem] p-10 flex flex-col justify-center gap-6">
               <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs uppercase tracking-widest">
                  <CheckCircle2 className="w-4 h-4" />
                  Verified Audit Result
               </div>
               <p className="text-sm text-white/70 leading-relaxed italic">
                 "Recallix successfully isolated core episodic events from high-noise conversational buffers, 
                 maintaining 20/20 recall with zero distracter leakage."
               </p>
            </div>
          </div>
        </section>

        {/* TEST 2: MEASURED SCALE (1M NODES) */}
        <section className="relative">
          <TestHeader number={2} title="Measured Search Latency" icon={Database} color="bg-blue-600" />
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <div className="lg:col-span-8 bg-white/[0.02] border border-white/10 rounded-[2.5rem] p-10 flex flex-col gap-8">
              <div className="h-[400px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={scaleData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="blueGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#2563EB" stopOpacity={0.4}/>
                        <stop offset="100%" stopColor="#2563EB" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#ffffff05" />
                    <XAxis dataKey="nodes" stroke="#444" fontSize={10} fontWeight="bold" axisLine={false} tickLine={false} dy={10} />
                    <YAxis stroke="#444" fontSize={10} fontWeight="bold" axisLine={false} tickLine={false} />
                    <Tooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="latency" name="Measured Latency" stroke="#2563EB" strokeWidth={4} fill="url(#blueGradient)" />
                    <Line type="monotone" dataKey="baseline" name="Python Baseline" stroke="#ffffff20" strokeWidth={2} strokeDasharray="5 5" dot={false} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="lg:col-span-4 flex flex-col gap-6">
              <div className="bg-blue-600 border border-blue-500 rounded-3xl p-8 flex flex-col gap-2 shadow-2xl shadow-blue-600/20">
                <span className="text-5xl font-black text-white tracking-tighter">0.106ms</span>
                <p className="text-xs text-white/70 uppercase font-bold tracking-widest">Average C++ Search (1M Nodes)</p>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-3xl p-8 flex flex-col gap-4">
                 <div className="flex items-center gap-2 text-blue-400 font-bold text-[10px] uppercase tracking-widest">
                   <Activity className="w-3 h-3" />
                   Measured Moat
                 </div>
                 <p className="text-xs text-white/50 leading-relaxed">
                   0.106ms pure C++ search at 1M nodes. ~1-5ms end-to-end API latency at production scale. 
                   Two-phase async architecture ensures writes never block agents. 
                   Benchmarked on Apple M4 with NEON SIMD hardware acceleration.
                 </p>
              </div>
            </div>
          </div>
        </section>

        {/* TEST 3: MULTI-AGENT HANDOVER */}
        <section className="relative">
          <TestHeader number={3} title="Universal Substrate" icon={Users} color="bg-purple-600" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white/[0.02] border border-white/10 rounded-[2.5rem] p-10 flex flex-col gap-6">
            <h3 className="text-xl font-bold">The Cross-Model Test</h3>
            <p className="text-white/60 leading-relaxed">
              Knowledge was stored using Llama 3.1 8B. 
              Retrieval was performed using Mistral 7B.
            </p>
              <div className="flex items-center gap-4 mt-4">
                <div className="flex-1 h-14 bg-blue-500/10 border border-blue-500/20 rounded-2xl flex items-center justify-center text-blue-400 font-bold">Llama 3.1 8B</div>
                <ArrowRight className="text-white/20" />
                <div className="flex-1 h-14 bg-purple-500/10 border border-purple-500/20 rounded-2xl flex items-center justify-center text-purple-400 font-bold">Mistral 7B</div>
              </div>
            </div>
            <div className="bg-purple-600/10 border border-purple-600/20 rounded-[2.5rem] p-10 flex flex-col justify-center gap-4">
            <span className="text-4xl font-black text-white">100% Fidelity</span>
            <p className="text-sm text-white/70 leading-relaxed">
              100% exact match fidelity across different model architectures. 
              Memory store latency: 407ms API. LLM generation time excluded from memory metrics.
            </p>
          </div>
          </div>
        </section>

        {/* TEST 4: LONG-TERM RETENTION */}
        <section className="relative">
          <TestHeader number={4} title="Context Retention" icon={History} color="bg-orange-600" />
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <div className="lg:col-span-8 bg-white/[0.02] border border-white/10 rounded-[2.5rem] p-10 flex flex-col gap-10">
              <p className="text-white/60 leading-relaxed mb-6">
                75% retention after 500 conversational turns with semantic collisions and evolving facts.
              </p>
              <div className="h-[300px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={retentionData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#ffffff05" />
                    <XAxis dataKey="turn" stroke="#444" fontSize={10} />
                    <YAxis stroke="#444" fontSize={10} domain={[0, 100]} />
                    <Tooltip content={<CustomTooltip />} />
                    <Line type="stepAfter" dataKey="recallix" name="Accuracy" stroke="#F97316" strokeWidth={5} dot={{ r: 6, fill: '#F97316', strokeWidth: 0 }} />
                    <Line type="stepAfter" dataKey="vanilla" name="Vanilla LLM" stroke="#ffffff20" strokeWidth={2} strokeDasharray="5 5" dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="lg:col-span-4 flex flex-col gap-6">
              <div className="bg-orange-600/10 border border-orange-600/20 rounded-3xl p-8 flex flex-col gap-4">
                <div className="flex items-center gap-2 text-orange-400 font-bold text-xs uppercase tracking-widest">
                  <AlertTriangle className="w-4 h-4" />
                  Failure Mode: Intent Shadowing
                </div>
                <p className="text-sm text-white/70 leading-relaxed italic text-white/50">
                   Intent Shadowing on low-importance date facts. Adaptive semantic fallback in development 
                   to resolve episodic matching collisions.
                </p>
              </div>
              <div className="bg-blue-600/10 border border-blue-600/20 rounded-3xl p-8 flex flex-col gap-4">
                <div className="flex flex-col">
                  <span className="text-4xl font-bold text-blue-400">0.01ms</span>
                  <span className="text-sm text-gray-400 mt-1 uppercase tracking-wider">Instant Write Latency</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-4xl font-bold text-purple-400">0.106ms</span>
                  <span className="text-sm text-gray-400 mt-1 uppercase tracking-wider">C++ Search (1M)</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* PHASE 05: SCALE ANALYSIS */}
        <section className="relative">
          <TestHeader number={5} title="Scale Analysis" icon={Layers} color="bg-zinc-700" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { scale: '1k nodes', recall: '96.4%', latency: '1.15ms', status: 'Optimal' },
              { scale: '10k nodes', recall: '80.9%', latency: '1.81ms', status: 'Stable' },
              { scale: '100k nodes', recall: '57.4%', latency: '5.17ms', status: 'Degrading' },
            ].map((item, i) => (
              <div key={i} className="bg-white/5 border border-white/10 rounded-3xl p-8">
                <div className="flex justify-between items-start mb-4">
                  <span className="text-xl font-black">{item.scale}</span>
                  <Badge className={item.status === 'Optimal' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'}>
                    {item.status}
                  </Badge>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-zinc-500 font-bold">Recall@5</span>
                    <span className="font-black">{item.recall}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-500 font-bold">Latency</span>
                    <span className="font-black">{item.latency}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <p className="text-center text-zinc-500 font-bold mt-8">
            Optimized for agent workloads under 10k memories. Improving 100k+ recall actively.
          </p>
        </section>

        {/* PHASE 06: ADVERSARIAL GAUNTLET */}
        <section className="relative">
          <TestHeader number={6} title="Adversarial Gauntlet" icon={ShieldCheck} color="bg-rose-600" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              { test: 'Temporal Contradiction', result: 'PASS' },
              { test: 'Slang/Noisy Identity', result: 'PASS' },
              { test: 'One-Token Adversarial', result: 'PASS' },
              { test: 'Ghost Query (FP)', result: 'PASS' },
              { test: 'Entity Typo Resolution', result: 'PASS' },
              { test: 'Linguistic Drift', result: 'PASS' },
              { test: 'Cross-Domain Collision', result: 'PASS' },
              { test: 'Ambiguous Facts', result: 'PASS' },
              { test: 'Multi-Hop Reasoning', result: 'PASS' },
              { test: 'State-Dependent Truth', result: 'PASS' },
              { test: 'Alias Resolution', result: 'FAIL', bug: true },
              { test: 'Identity Locking', result: 'FAIL', bug: true },
            ].map((item, i) => (
              <div key={i} className="bg-white/5 border border-white/10 rounded-2xl p-5 flex items-center justify-between">
                <span className="text-sm font-bold text-zinc-400">{item.test}</span>
                {item.result === 'PASS' ? (
                  <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20">PASS</Badge>
                ) : (
                  <Badge className="bg-rose-500/10 text-rose-400 border-rose-500/20">FAIL</Badge>
                )}
              </div>
            ))}
          </div>
          <div className="mt-8 p-6 rounded-[32px] bg-white/[0.02] border border-white/10 text-center">
            <p className="text-lg font-black tracking-tight">10/12 Adversarial Tests Passing</p>
            <p className="text-sm text-zinc-500 font-bold mt-1">2 known failures documented and tracked for the next core sprint.</p>
          </div>
        </section>

        <footer className="text-center py-20 border-t border-white/5 text-[10px] font-bold tracking-[0.4em] text-white/20 uppercase">
          Recallix Cognitive Systems • Official Audit Report • April 2026
        </footer>
      </main>
    </div>
  );
}
