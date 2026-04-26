"use client";

import React from "react";
import { motion } from "framer-motion";
import {
  Brain, Cpu, Database, GitBranch, Layers,
  ArrowLeft, ChevronRight, Sparkles, Clock,
  Search, Shield, RefreshCw, Lightbulb, Zap,
  Activity, Target, Workflow, Eye, Boxes,
  Microchip, Dna, HardDrive, ShieldCheck,
  AlertTriangle, FlaskConical, Construction,
  Network, Lock, Layers as LayersIcon
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
};

const roadmapSections = [
  {
    title: "Honest Technical Debt",
    desc: "Things that are currently broken or suboptimal.",
    icon: AlertTriangle,
    color: "rose",
    tasks: [
      { name: "SQLite Bottleneck", detail: "WAL mode locks under concurrent agent writes. Migration to RocksDB/Postgres required for scale.", status: "critical" },
      { name: "Heuristic Ranking", detail: "ImportanceRanker is fragile and regex-based. Fails on nuanced date/time contexts.", status: "bug" },
      { name: "Regex Intent Detection", detail: "Sub-optimal accuracy. Defaulting to 'conversational' too often. Needs MiniLM classifier.", status: "debt" },
      { name: "SIMD Portability", detail: "NEON only. x86 falls back to scalar. AVX2 implementation required for cloud parity.", status: "debt" },
    ]
  },
  {
    title: "Algorithmic Moats",
    desc: "Pure performance and efficiency breakthroughs.",
    icon: Microchip,
    color: "purple",
    tasks: [
      { name: "Parallel HNSW Construction", detail: "OpenMP integration to inserts. Targeting 4-8x faster build times.", status: "planned" },
      { name: "Product Quantization", detail: "4x memory reduction via 8-bit vector compression. Essential for 10M+ nodes.", status: "researching" },
      { name: "Adaptive efSearch", detail: "Dynamic precision tuning per query type. High speed for simple, high recall for complex.", status: "planned" },
      { name: "Background Graph Pruning", detail: "Remove low-importance/stale nodes automatically to keep the index lean.", status: "planned" },
    ]
  },
  {
    title: "Memory Architecture",
    desc: "Human-inspired cognitive evolution.",
    icon: Brain,
    color: "cyan",
    tasks: [
      { name: "Ebbinghaus Spaced Repetition", detail: "Memories decay unless reinforced. Frequently retrieved facts get importance boosts.", status: "in-progress" },
      { name: "Semantic Deduplication", detail: "Merge similar episodic events instead of duplicating logs. Keeps the graph clean.", status: "planned" },
      { name: "Idle Consolidation", detail: "Mimic human sleep: Cluster and promote memories during system idle cycles.", status: "planned" },
      { name: "Dynamic Working Buffer", detail: "Expand/contract working memory size based on active task cognitive load.", status: "researching" },
    ]
  },
  {
    title: "Multi-Agent Governance",
    desc: "Scale and safety for agent ecosystems.",
    icon: Network,
    color: "emerald",
    tasks: [
      { name: "Shared Permissions Layer", detail: "Private vs Global memory flags. Mandatory for enterprise multi-agent use.", status: "planned" },
      { name: "Conflict Resolution", detail: "Detect contradictory facts between agents and trigger resolution workflows.", status: "planned" },
      { name: "Agent Provenance", detail: "Full versioning of who wrote which memory and when for auditability.", status: "planned" },
    ]
  },
  {
    title: "Infrastructure & Research",
    desc: "Enterprise scale and academic breakthroughs.",
    icon: FlaskConical,
    color: "amber",
    tasks: [
      { name: "mmap Persistence", detail: "Eliminate 15min rebuilds. Map HNSW index directly to disk for instant loads.", status: "critical" },
      { name: "Distributed Sharding", detail: "Partition HNSW across nodes. The path to 100M+ node cognitive substrates.", status: "researching" },
      { name: "Learned Importance", detail: "Train ranker on retrieval success/failure signals to self-correct over time.", status: "researching" },
      { name: "Embedding Alignment", detail: "Map disparate agent embedding spaces to a shared cognitive substrate.", status: "researching" },
    ]
  }
];

const statusColors: Record<string, string> = {
  critical: "text-rose-400 bg-rose-500/10 border-rose-500/20",
  bug: "text-orange-400 bg-orange-500/10 border-orange-500/20",
  debt: "text-zinc-400 bg-zinc-500/10 border-zinc-500/20",
  planned: "text-blue-400 bg-blue-500/10 border-blue-500/20",
  "in-progress": "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",
  researching: "text-purple-400 bg-purple-500/10 border-purple-500/20",
};

export default function RoadmapPage() {
  return (
    <div className="min-h-screen bg-[#050506] text-white selection:bg-cyan-500/30">
      <nav className="fixed top-0 left-0 right-0 z-50 h-16 border-b border-white/5 flex items-center justify-between px-8 glass backdrop-blur-2xl">
        <div className="flex items-center gap-3 cursor-pointer">
          <Link href="/" className="flex items-center gap-3">
            <Brain className="w-6 h-6 text-cyan-400" />
            <span className="text-xl font-black tracking-tighter">RECALLIX</span>
          </Link>
        </div>
        <div className="hidden md:flex items-center gap-6">
          <Link href="/architecture" className="text-sm font-bold text-zinc-400 hover:text-white transition-colors">Architecture</Link>
          <Link href="/benchmark" className="text-sm font-bold text-zinc-400 hover:text-white transition-colors">Performance Audit</Link>
          <Link href="/roadmap" className="text-sm font-bold text-white transition-colors">Roadmap</Link>
          <Link href="/observability" className="text-sm font-bold text-zinc-400 hover:text-white transition-colors">Observability</Link>
        </div>
        <Link href="/benchmark">
          <Button className="h-10 px-5 bg-cyan-500 hover:bg-cyan-400 text-black font-black rounded-full">
            View Audit
          </Button>
        </Link>
      </nav>

      <main className="pt-32 pb-24 container mx-auto px-6 max-w-7xl">
        <header className="max-w-3xl mb-24">
          <Badge className="mb-6 py-1.5 px-4 bg-orange-500/10 border-orange-500/20 text-orange-400 rounded-full font-bold text-xs uppercase tracking-widest">
            Transparency Manifest
          </Badge>
          <h1 className="text-6xl md:text-8xl font-black tracking-tighter leading-[0.85] mb-8">
            The Path To <br />
            <span className="text-gradient">Production.</span>
          </h1>
          <p className="text-xl text-zinc-500 font-bold leading-relaxed max-w-2xl">
            We're not just building a vector database. We're building a cognitive OS. 
            Here is every bottleneck we've identified and every algorithm we're deploying to solve it.
          </p>
        </header>

        <motion.div 
          variants={container}
          initial="hidden"
          animate="show"
          className="space-y-32"
        >
          {roadmapSections.map((section, idx) => (
            <motion.section key={section.title} variants={item} className="relative">
              <div className="flex flex-col md:flex-row gap-12 lg:gap-24">
                <div className="md:w-1/3">
                  <div className={`w-14 h-14 rounded-2xl bg-${section.color}-500/10 border border-${section.color}-500/20 flex items-center justify-center mb-6`}>
                    <section.icon className={`w-7 h-7 text-${section.color}-400`} />
                  </div>
                  <h2 className="text-3xl font-black tracking-tight mb-4">{section.title}</h2>
                  <p className="text-zinc-500 font-bold leading-relaxed">
                    {section.desc}
                  </p>
                </div>
                
                <div className="md:w-2/3 grid grid-cols-1 gap-4">
                  {section.tasks.map((task) => (
                    <div key={task.name} className="glass-card rounded-[32px] p-8 border border-white/5 hover:border-white/10 transition-all group relative overflow-hidden">
                      <div className="flex items-start justify-between mb-4 relative z-10">
                        <h4 className="text-lg font-black text-white">{task.name}</h4>
                        <Badge className={`py-1 px-3 rounded-full text-[10px] font-black uppercase tracking-widest ${statusColors[task.status]}`}>
                          {task.status}
                        </Badge>
                      </div>
                      <p className="text-sm text-zinc-500 font-bold leading-relaxed relative z-10">
                        {task.detail}
                      </p>
                      {/* Interactive pulsed dot for in-progress or critical */}
                      {(task.status === 'in-progress' || task.status === 'critical') && (
                        <div className="absolute top-8 right-8">
                           <div className={`w-2 h-2 rounded-full ${task.status === 'critical' ? 'bg-rose-500' : 'bg-cyan-500'} animate-ping opacity-50`} />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </motion.section>
          ))}
        </motion.div>

        <section className="py-32 text-center">
           <div className="max-w-2xl mx-auto">
              <h2 className="text-4xl md:text-6xl font-black tracking-tighter mb-8 leading-tight">
                Help Us Build the <br />
                <span className="text-gradient">Memory Standard.</span>
              </h2>
              <p className="text-zinc-500 font-bold mb-12">
                We're open sourcing our technical debt and our research direction. 
                Contributions are welcome on every milestone above.
              </p>
              <div className="flex justify-center gap-4">
                 <Link href="/architecture">
                    <Button variant="outline" className="h-14 px-8 border-white/10 font-black rounded-2xl">
                       Back to Architecture
                    </Button>
                 </Link>
                 <Link href="https://github.com/AyishikD/Recallix">
                    <Button className="h-14 px-8 bg-white text-black font-black rounded-2xl hover:bg-zinc-200">
                       Star on GitHub
                    </Button>
                 </Link>
              </div>
           </div>
        </section>
      </main>

      <footer className="border-t border-white/5 py-8 px-8 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-zinc-600" />
          <span className="text-xs font-bold text-zinc-600">RECALLIX ROADMAP</span>
        </div>
        <span className="text-xs text-zinc-700">Transparency is the only path to a shared intelligence.</span>
      </footer>
    </div>
  );
}
