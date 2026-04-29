"use client";

import React, { useRef, useState, useEffect } from "react";
import { motion, useInView, AnimatePresence } from "framer-motion";
import {
  Brain, Cpu, Database, Search, Clock, Lightbulb,
  Code2, Activity, ArrowRight, Layers, Sparkles,
  Shield, TrendingUp, Target, AlertTriangle, Play,
  Workflow, Eye, ChevronRight, CheckCircle2, Zap,
  ShieldCheck, Users, History, Github
} from "lucide-react";
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

const fadeUp = { hidden: { opacity: 0, y: 30 }, visible: { opacity: 1, y: 0 } };

function AnimatedSection({ children, className = "", delay = 0 }: { children: React.ReactNode; className?: string; delay?: number }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });
  return (
    <motion.div ref={ref} variants={fadeUp} initial="hidden" animate={inView ? "visible" : "hidden"} transition={{ duration: 0.6, delay }} className={className}>
      {children}
    </motion.div>
  );
}

// Chart Data points for Audit sections
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
        <p className="text-white/50 text-xs font-mono mb-2">{label} {typeof label === 'number' && label > 500 ? 'NODES' : 'TURN'}</p>
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
            <span className="text-sm font-bold" style={{ color: entry.color }}>
              {entry.name}: {entry.value}{entry.name.includes('Accuracy') || entry.name.includes('Retention') ? '%' : 'ms'}
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

const demoConversation = [
  { user: "My name is Alex and I'm a software engineer", time: "Day 1" },
  { user: "I'm allergic to peanuts — please remember this", time: "Day 3" },
  { user: "I have a meeting with Sarah next Tuesday", time: "Day 5" },
  { user: "What's my name?", time: "Day 7" },
];

const withoutResponses = [
  "Stored.",
  "Noted.",
  "Got it.",
  "I'm sorry, I don't have that information. Could you tell me your name?",
];

const withMemoizeResponses = [
  "Intent: Learning → Stored in Episodic + Semantic  ✓",
  "Intent: Preference → Importance: 9.5 → Long-Term  ✓",
  "Intent: Task → Calendar Schema detected → Timeline  ✓",
  "You're Alex! (Recalled in 0.1ms from Long-Term Memory)",
];

function ProblemSolutionDemo() {
  const [step, setStep] = useState(-1);
  const [phase, setPhase] = useState<"intro" | "playing" | "done">("intro");
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  useEffect(() => {
    if (!inView) return;
    const t = setTimeout(() => { setPhase("playing"); setStep(0); }, 2000);
    return () => clearTimeout(t);
  }, [inView]);

  useEffect(() => {
    if (phase !== "playing" || step < 0) return;
    if (step >= demoConversation.length) {
      const t = setTimeout(() => setPhase("done"), 2500);
      return () => clearTimeout(t);
    }
    const t = setTimeout(() => setStep((s) => s + 1), 2800);
    return () => clearTimeout(t);
  }, [step, phase]);

  useEffect(() => {
    if (phase !== "done") return;
    const t = setTimeout(() => {
      setStep(-1);
      setPhase("intro");
      setTimeout(() => { setPhase("playing"); setStep(0); }, 1500);
    }, 5000);
    return () => clearTimeout(t);
  }, [phase]);

  return (
    <section ref={ref} className="py-28 px-6 max-w-6xl mx-auto">
      <AnimatedSection className="text-center mb-14">
        <Badge className="mb-4 py-1.5 px-4 bg-red-500/10 border-red-500/20 text-red-400 rounded-full font-bold text-xs">
          THE CORE PROBLEM
        </Badge>
        <h2 className="text-4xl md:text-6xl font-black tracking-tighter mb-4">
          See the <span className="text-gradient">Difference</span>
        </h2>
        <p className="text-zinc-500 text-lg font-bold max-w-xl mx-auto">
          Same conversation. Same 7 days. Completely different outcomes.
        </p>
      </AnimatedSection>

      <AnimatePresence>
        {phase === "intro" && inView && (
          <motion.div
            key="intro-blast"
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.5 }}
            transition={{ duration: 0.5 }}
            className="flex flex-col items-center justify-center py-24 gap-6"
          >
            <div className="relative">
              <motion.div
                animate={{ scale: [1, 1.6, 1], opacity: [0.3, 0.6, 0.3] }}
                transition={{ repeat: Infinity, duration: 1.5 }}
                className="absolute -inset-10 bg-cyan-500/15 rounded-full blur-3xl"
              />
              <motion.div
                animate={{ scale: [1, 1.3, 1], opacity: [0.2, 0.5, 0.2] }}
                transition={{ repeat: Infinity, duration: 1.5, delay: 0.3 }}
                className="absolute -inset-16 bg-purple-500/10 rounded-full blur-3xl"
              />
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                className="relative w-28 h-28 rounded-full border-[3px] border-zinc-800 border-t-cyan-400 flex items-center justify-center"
              >
                <Play className="w-10 h-10 text-cyan-400 ml-1" />
              </motion.div>
            </div>
            <motion.p
              animate={{ opacity: [0.4, 1, 0.4] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
              className="text-xs font-black uppercase tracking-[0.3em] text-zinc-600"
            >
              Loading Demo
            </motion.p>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {phase !== "intro" && (
          <motion.div
            key="demo-panels"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-5"
          >
            <div className="rounded-[28px] border border-red-500/10 bg-zinc-950/50 p-7 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-48 h-48 bg-red-500/5 blur-[80px] rounded-full" />
              <div className="flex items-center gap-2 mb-7 relative z-10">
                <AlertTriangle className="w-4 h-4 text-red-400" />
                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-red-400">Without Memory</span>
                <Badge className="ml-auto text-[8px] bg-zinc-900 border-zinc-800 text-zinc-600 font-black">STANDARD LLM</Badge>
              </div>
              <div className="space-y-4 min-h-[340px] relative z-10">
                {demoConversation.map((msg, i) => (
                  <AnimatePresence key={`without-${i}`}>
                    {step > i && (
                      <motion.div
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: phase === "done" ? 0.3 : 1, y: 0 }}
                        transition={{ duration: 0.4 }}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <div className="w-1 h-1 rounded-full bg-zinc-700" />
                          <span className="text-[9px] font-bold text-zinc-600">{msg.time}</span>
                        </div>
                        <div className="pl-3 border-l-2 border-zinc-800/60">
                          <p className="text-xs font-bold text-zinc-400 mb-1">{msg.user}</p>
                          <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}
                            className={`text-[11px] font-bold ${i === 3 ? "text-red-400" : "text-zinc-600"}`}>
                            → {withoutResponses[i]}
                          </motion.p>
                        </div>
                      </motion.div>
                    )}
                    {step === i && (
                      <motion.div key={`typing-w-${i}`} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
                        <div className="flex items-center gap-2 mb-1">
                          <div className="w-1 h-1 rounded-full bg-zinc-700" />
                          <span className="text-[9px] font-bold text-zinc-600">{msg.time}</span>
                        </div>
                        <div className="pl-3 border-l-2 border-zinc-800/60">
                          <p className="text-xs font-bold text-zinc-400">{msg.user}</p>
                          <div className="flex gap-1.5 mt-2">
                            {[0, 1, 2].map((d) => (
                              <motion.div key={d} animate={{ scale: [1, 1.4, 1] }} transition={{ repeat: Infinity, duration: 0.6, delay: d * 0.15 }} className="w-1.5 h-1.5 rounded-full bg-zinc-700" />
                            ))}
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                ))}
                {phase === "done" && (
                  <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="mt-8 p-4 rounded-2xl bg-red-500/5 border border-red-500/10 text-center">
                    <p className="text-sm font-black text-red-400">❌ Total Memory Loss</p>
                    <p className="text-[10px] font-bold text-red-400/60 mt-1">The agent forgot the user&apos;s name after just 7 days.</p>
                  </motion.div>
                )}
              </div>
            </div>

            <div className="rounded-[28px] border border-cyan-500/10 bg-zinc-950/50 p-7 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-48 h-48 bg-cyan-500/5 blur-[80px] rounded-full" />
              <div className="flex items-center gap-2 mb-7 relative z-10">
                <Brain className="w-4 h-4 text-cyan-400" />
                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-cyan-400">With Recallix</span>
                <Badge className="ml-auto text-[8px] bg-cyan-500/5 border-cyan-500/10 text-cyan-500 font-black">COGNITIVE MEMORY</Badge>
              </div>
              <div className="space-y-4 min-h-[340px] relative z-10">
                {demoConversation.map((msg, i) => (
                  <AnimatePresence key={`with-${i}`}>
                    {step > i && (
                      <motion.div
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.4 }}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} className="w-1.5 h-1.5 rounded-full bg-cyan-500" />
                          <span className="text-[9px] font-bold text-zinc-600">{msg.time}</span>
                          {i === 1 && <Badge className="text-[7px] py-0 px-1.5 bg-amber-500/10 border-amber-500/20 text-amber-400 font-black">CRITICAL</Badge>}
                        </div>
                        <div className="pl-3 border-l-2 border-cyan-500/20">
                          <p className="text-xs font-bold text-zinc-400 mb-1">{msg.user}</p>
                          <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}
                            className={`text-[11px] font-bold ${i === 3 ? "text-cyan-400" : "text-cyan-600"}`}>
                            → {withMemoizeResponses[i]}
                          </motion.p>
                        </div>
                      </motion.div>
                    )}
                    {step === i && (
                      <motion.div key={`typing-m-${i}`} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
                        <div className="flex items-center gap-2 mb-1">
                          <div className="w-1.5 h-1.5 rounded-full bg-cyan-500/50 animate-pulse" />
                          <span className="text-[9px] font-bold text-zinc-600">{msg.time}</span>
                        </div>
                        <div className="pl-3 border-l-2 border-cyan-500/20">
                          <p className="text-xs font-bold text-zinc-400">{msg.user}</p>
                          <div className="flex gap-1.5 mt-2">
                            {[0, 1, 2].map((d) => (
                              <motion.div key={d} animate={{ scale: [1, 1.4, 1] }} transition={{ repeat: Infinity, duration: 0.6, delay: d * 0.15 }} className="w-1.5 h-1.5 rounded-full bg-cyan-700" />
                            ))}
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                ))}
                {phase === "done" && (
                  <motion.div initial={{ opacity: 0, y: 8, scale: 0.95 }} animate={{ opacity: 1, y: 0, scale: 1 }} className="mt-8 p-4 rounded-2xl bg-cyan-500/5 border border-cyan-500/10 text-center">
                    <p className="text-sm font-black text-cyan-400">✅ Neural-Heuristic Recall</p>
                    <p className="text-[10px] font-bold text-cyan-500/60 mt-1">Stored across 6 layers · Hybrid Reranked · 0.1ms recall</p>
                    <div className="flex items-center justify-center gap-5 mt-3">
                      <span className="text-[9px] font-black text-zinc-600">🧠 9 stages</span>
                      <span className="text-[9px] font-black text-zinc-600">📊 HNSW</span>
                      <span className="text-[9px] font-black text-zinc-600">⚡ NEON SIMD</span>
                      <span className="text-[9px] font-black text-zinc-600">🔗 SQLite WAL</span>
                    </div>
                  </motion.div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
}

const features = [
  { icon: Database, title: "Shared Substrate", desc: "A unified memory layer accessible by any agent architecture, bridging the gap between Llama, Mistral, and GPT ecosystems.", color: "cyan" },
  { icon: Search, title: "Model Interoperability", desc: "Zero-loss context handover. Store with a reasoning model, retrieve with a coding assistant, or scale across thousands of specialized agents.", color: "blue" },
  { icon: Clock, title: "Universal Continuity", desc: "True cross-session persistence. Your agents maintain a permanent cognitive history that evolves as your user does.", color: "purple" },
  { icon: Lightbulb, title: "Reflection Insights", desc: "Background LLM threads extract behavioral patterns and high-level insights from raw episodic logs.", color: "amber" },
  { icon: Sparkles, title: "Meta-Memory", desc: "Self-optimizing retrieval policies and schema evolution that adapts to user-specific interaction patterns.", color: "emerald" },
  { icon: ShieldCheck, title: "Hardware Moat", desc: "C++ HNSW engines with Cross-Platform SIMD acceleration (AVX2/SSE/NEON). Millisecond search at 1,000,000 nodes.", color: "rose" },
  { icon: Activity, title: "Observability", desc: "Full system metrics: memory growth, recall latency, cluster health, schema evolution.", color: "orange" },
  { icon: Shield, title: "Local-First", desc: "No cloud dependencies. All models run locally via Ollama. Data never leaves your machine.", color: "teal" },
];

const colorMap: Record<string, string> = {
  cyan: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",
  blue: "text-blue-400 bg-blue-500/10 border-blue-500/20",
  purple: "text-purple-400 bg-purple-500/10 border-purple-500/20",
  amber: "text-amber-400 bg-amber-500/10 border-amber-500/20",
  emerald: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  rose: "text-rose-400 bg-rose-500/10 border-rose-500/20",
  orange: "text-orange-400 bg-orange-500/10 border-orange-500/20",
  teal: "text-teal-400 bg-teal-500/10 border-teal-500/20",
};

const pipelineStages = [
  { name: "Input", icon: <Eye className="w-3.5 h-3.5" />, color: "cyan" },
  { name: "Intent Engine", icon: <Target className="w-3.5 h-3.5" />, color: "rose" },
  { name: "Sensory", icon: <Eye className="w-3.5 h-3.5" />, color: "blue" },
  { name: "Working", icon: <Brain className="w-3.5 h-3.5" />, color: "purple" },
  { name: "Episodic", icon: <Database className="w-3.5 h-3.5" />, color: "cyan" },
  { name: "Semantic", icon: <Cpu className="w-3.5 h-3.5" />, color: "orange" },
  { name: "Long-Term", icon: <Shield className="w-3.5 h-3.5" />, color: "emerald" },
  { name: "Reflection", icon: <Lightbulb className="w-3.5 h-3.5" />, color: "amber" },
  { name: "Meta", icon: <Sparkles className="w-3.5 h-3.5" />, color: "rose" },
];

function HeroPipeline() {
  const [active, setActive] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setActive(a => (a + 1) % pipelineStages.length), 1200);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="glass-card rounded-[32px] p-8 md:p-12 relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_top,rgba(34,211,238,0.04)_0%,transparent_50%)]" />
      <div className="flex items-center justify-between mb-6 relative z-10">
        <div className="text-[10px] font-black uppercase tracking-widest text-zinc-600">MEMORY PIPELINE — REAL-TIME FLOW</div>
        <Link href="/flow-control">
          <span className="text-[10px] font-bold text-cyan-400 hover:text-cyan-300 flex items-center gap-1 cursor-pointer transition-colors">
            See Full Pipeline <ChevronRight className="w-3 h-3" />
          </span>
        </Link>
      </div>
      <div className="flex flex-wrap justify-center gap-3 md:gap-x-0 md:gap-y-4 relative z-10">
        {pipelineStages.map((stage, i) => (
          <motion.div key={stage.name} className="flex items-center">
            <motion.div
              animate={{
                borderColor: active === i ? "rgba(34,211,238,0.6)" : "rgba(63,63,70,0.5)",
                backgroundColor: active === i ? "rgba(34,211,238,0.08)" : "rgba(39,39,42,0.6)",
                scale: active === i ? 1.08 : 1,
                boxShadow: active === i ? "0 0 20px rgba(34,211,238,0.15)" : "none",
              }}
              transition={{ duration: 0.4, ease: "easeOut" }}
              className="px-3 py-2 md:px-4 md:py-2.5 rounded-xl border text-xs font-black flex items-center gap-2 cursor-default"
            >
              <span className={active === i ? "text-cyan-400" : "text-zinc-500"}>{stage.icon}</span>
              <span className={active === i ? "text-cyan-300" : "text-zinc-400"}>{stage.name}</span>
            </motion.div>
            {i < pipelineStages.length - 1 && (
              <div className="hidden md:flex items-center mx-1 w-6 relative">
                <div className="w-full h-px bg-zinc-700" />
                {active === i && (
                  <motion.div
                    className="absolute w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_6px_rgba(34,211,238,0.6)]"
                    initial={{ left: 0, opacity: 0 }}
                    animate={{ left: "100%", opacity: [0, 1, 1, 0] }}
                    transition={{ duration: 0.8, ease: "easeInOut" }}
                  />
                )}
              </div>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
}

const lifecycleDetailed = [
  { step: "Input", label: "User sends a message", detail: "Raw text enters the system via POST /memory/store API with API key authentication.", icon: <Eye className="w-5 h-5" />, system: "API", color: "from-cyan-500 to-blue-500" },
  { step: "Intent Engine", label: "Detects user's cognitive intent", detail: "Sub-10ms NLP classifier detects goal, preference, or research intent to guide recall strategy.", icon: <Target className="w-5 h-5" />, system: "Python", color: "from-rose-500 to-red-500" },
  { step: "Sensory Buffer", label: "60s TTL deque captures it", detail: "Bounded deque (maxlen=10) with 60-second time-to-live. Ultra-short-term iconic memory.", icon: <Eye className="w-5 h-5" />, system: "Python", color: "from-blue-500 to-indigo-500" },
  { step: "Working Memory", label: "Active context updated", detail: "Rolling conversation summary maintained in JSON. The AI's scratchpad for current session.", icon: <Brain className="w-5 h-5" />, system: "Python", color: "from-indigo-500 to-purple-500" },
  { step: "Episodic Storage", label: "Stored as timeline event", detail: "Persisted to SQLite (WAL mode) with importance scoring, reinforcement tracking, and keyword indexing.", icon: <Database className="w-5 h-5" />, system: "Python", color: "from-purple-500 to-violet-500" },
  { step: "Semantic Embedding", label: "Embedded in 128D vector space", detail: "128-dimensional vector generated and sent to C++ VectorEngine for cosine similarity indexing.", icon: <Cpu className="w-5 h-5" />, system: "C++", color: "from-orange-500 to-amber-500" },
  { step: "Long-Term Gate", label: "High-importance promoted", detail: "Memories scoring >8.0 importance are promoted to long-term storage with Ebbinghaus decay protection.", icon: <Shield className="w-5 h-5" />, system: "Python", color: "from-emerald-500 to-teal-500" },
  { step: "Reflection", label: "LLM generates insights", detail: "Background threads via diverse LLM architectures analyze memory patterns and generate high-level behavioral reflections.", icon: <Lightbulb className="w-5 h-5" />, system: "Ollama", color: "from-amber-500 to-yellow-500" },
  { step: "Meta-Memory", label: "System self-optimizes", detail: "Meta-analyzer evolves schemas, optimizes retrieval policies, and tunes attention weights autonomously for cross-model continuity.", icon: <Sparkles className="w-5 h-5" />, system: "Python", color: "from-rose-500 to-pink-500" },
];

function MemoryLifecycleSection() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });
  const [activeIdx, setActiveIdx] = useState(-1);
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  useEffect(() => {
    if (!inView) return;
    let i = 0;
    const interval = setInterval(() => {
      if (i < lifecycleDetailed.length) { setActiveIdx(i); i++; }
      else clearInterval(interval);
    }, 600);
    return () => clearInterval(interval);
  }, [inView]);

  return (
    <section ref={ref} className="py-28 px-6 max-w-5xl mx-auto">
      <AnimatedSection className="text-center mb-6">
        <Badge className="mb-4 py-1.5 px-4 bg-cyan-500/10 border-cyan-500/20 text-cyan-400 rounded-full font-bold text-xs">
          HOW IT WORKS
        </Badge>
        <h2 className="text-4xl md:text-5xl font-black tracking-tighter mb-4">
          The Memory <span className="text-gradient">Lifecycle</span>
        </h2>
        <p className="text-zinc-500 text-lg font-bold max-w-xl mx-auto">
          Every interaction flows through 9 cognitive stages.
        </p>
      </AnimatedSection>

      <div className="space-y-0">
        {lifecycleDetailed.map((stage, i) => (
          <motion.div
            key={stage.step}
            initial={{ opacity: 0, x: -20 }}
            animate={i <= activeIdx ? { opacity: 1, x: 0 } : { opacity: 0.2, x: -20 }}
            transition={{ duration: 0.5, delay: i * 0.05 }}
          >
            {i > 0 && (
              <div className="flex items-center ml-7 h-6">
                <motion.div
                  className="w-0.5 h-full"
                  animate={{
                    background: i <= activeIdx
                      ? "linear-gradient(to bottom, rgba(34,211,238,0.4), rgba(34,211,238,0.1))"
                      : "rgba(63,63,70,0.3)"
                  }}
                />
              </div>
            )}

            <motion.div
              onClick={() => setExpandedIdx(expandedIdx === i ? null : i)}
              className={`flex items-start gap-4 p-4 rounded-2xl cursor-pointer transition-all duration-300
                ${i <= activeIdx ? "hover:bg-zinc-900/50" : ""}`}
              whileHover={i <= activeIdx ? { x: 4 } : {}}
            >
              <motion.div
                className={`relative flex-shrink-0 w-14 h-14 rounded-2xl flex items-center justify-center
                  ${i <= activeIdx ? `bg-gradient-to-br ${stage.color} text-white shadow-lg` : "bg-zinc-900/50 text-zinc-600 border border-zinc-800/50"}`}
                animate={i === activeIdx && activeIdx < lifecycleDetailed.length ? { scale: [1, 1.1, 1] } : {}}
                transition={{ duration: 0.6 }}
              >
                {stage.icon}
                {i === activeIdx && activeIdx < lifecycleDetailed.length && (
                  <motion.div
                    className="absolute inset-0 rounded-2xl border-2 border-white/30"
                    animate={{ scale: [1, 1.3], opacity: [0.5, 0] }}
                    transition={{ duration: 1, repeat: Infinity }}
                  />
                )}
              </motion.div>

              <div className="flex-1 min-w-0 pt-1">
                <div className="flex items-center gap-3 flex-wrap">
                  <h3 className={`text-base font-black ${i <= activeIdx ? "text-white" : "text-zinc-600"}`}>
                    {stage.step}
                  </h3>
                  <Badge className={`text-[9px] py-0 px-2 ${i <= activeIdx
                    ? "bg-zinc-800/80 border-zinc-700/50 text-zinc-400"
                    : "bg-zinc-900/50 border-zinc-800/30 text-zinc-700"}`}>
                    {stage.system}
                  </Badge>
                  {i <= activeIdx && (
                    <ChevronRight className={`w-3.5 h-3.5 text-zinc-600 transition-transform ml-auto ${expandedIdx === i ? "rotate-90" : ""}`} />
                  )}
                </div>
                <p className={`text-sm font-bold mt-0.5 ${i <= activeIdx ? "text-zinc-400" : "text-zinc-700"}`}>
                  {stage.label}
                </p>

                <AnimatePresence>
                  {expandedIdx === i && i <= activeIdx && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3 }}
                      className="overflow-hidden"
                    >
                      <p className="text-xs text-zinc-500 mt-3 leading-relaxed border-t border-zinc-800/50 pt-3">
                        {stage.detail}
                      </p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          </motion.div>
        ))}
      </div>

      <AnimatedSection delay={0.3} className="mt-10 text-center">
        <Link href="/flow-control">
          <Button variant="outline" className="h-12 px-8 border-white/10 rounded-2xl font-bold hover:bg-white/5 gap-2">
            <Workflow className="w-4 h-4" />
            Explore Full 12-Stage Pipeline <ArrowRight className="w-4 h-4" />
          </Button>
        </Link>
      </AnimatedSection>
    </section>
  );
}

export default function HomePage() {
  return (
    <div className="min-h-screen bg-black text-white selection:bg-cyan-500/30 overflow-hidden">
      <nav className="fixed top-0 left-0 right-0 z-50 h-16 border-b border-white/5 flex items-center justify-between px-8 glass backdrop-blur-2xl">
        <div className="flex items-center gap-3 cursor-pointer">
          <Brain className="w-6 h-6 text-cyan-400" />
          <span className="text-xl font-black tracking-tighter">RECALLIX</span>
        </div>
        <div className="hidden md:flex items-center gap-6">
          <Link href="/architecture" className="text-sm font-bold text-zinc-400 hover:text-white transition-colors">Architecture</Link>
          <Link href="/benchmark" className="text-sm font-bold text-zinc-400 hover:text-white transition-colors">Performance Audit</Link>
          <Link href="/roadmap" className="text-sm font-bold text-zinc-400 hover:text-white transition-colors">Roadmap</Link>
          <Link href="/observability" className="text-sm font-bold text-zinc-400 hover:text-white transition-colors">Observability</Link>
        </div>
      </nav>

      <section className="relative pt-40 pb-24 px-6 text-center">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(34,211,238,0.08)_0%,transparent_60%)]" />
        <AnimatedSection>
          <Badge className="mb-6 py-2 px-4 bg-cyan-500/10 border-cyan-500/20 text-cyan-400 rounded-full font-bold">
            ✨ The Cognitive Memory Infrastructure for AI
          </Badge>
        </AnimatedSection>
        <AnimatedSection delay={0.1}>
          <h1 className="text-5xl md:text-7xl lg:text-8xl font-black tracking-tighter max-w-5xl mx-auto leading-[0.9] mb-8">
            Universal Memory{" "}
            <span className="text-gradient">Substrate</span>{" "}
            for Multi-Agent Systems
          </h1>
        </AnimatedSection>
        <AnimatedSection delay={0.2}>
          <p className="text-xl md:text-2xl text-zinc-500 font-bold max-w-3xl mx-auto mb-12 leading-relaxed">
            0.01ms writes. Sub-2ms search.<br />
            The first verified cross-model memory substrate for AI agents.
          </p>
        </AnimatedSection>
        <AnimatedSection delay={0.3} className="relative z-10">
          <div className="flex flex-wrap gap-4 justify-center relative z-10">
            <Link href="/architecture">
              <Button className="h-14 px-8 bg-white text-black font-black text-lg rounded-2xl hover:bg-zinc-200">
                View Architecture <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </Link>
            <Link href="/benchmark">
              <Button variant="outline" className="h-14 px-8 border-white/10 text-white font-black text-lg rounded-2xl hover:bg-white/5">
                View Performance Audit
              </Button>
            </Link>
            <Link href="https://github.com/AyishikD/Recallix">
              <Button variant="outline" className="h-14 px-8 border-white/10 text-white font-black text-lg rounded-2xl hover:bg-white/5 gap-2">
                <Github className="w-5 h-5" /> Star on GitHub
              </Button>
            </Link>
          </div>
        </AnimatedSection>

        <AnimatedSection delay={0.4} className="mt-24 max-w-4xl mx-auto">
          <HeroPipeline />
        </AnimatedSection>
      </section>

      {/* STATS OVERVIEW */}
      <section className="relative max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-4 gap-6 py-12">
        {[
          { label: 'Writes', value: '0.01ms', unit: '', icon: Zap, color: 'text-blue-400' },
          { label: 'Recall@5 (1k nodes)', value: '96.4%', unit: '', icon: Activity, color: 'text-purple-400' },
          { label: 'Multi-Agent Fidelity', value: '100%', unit: '', icon: Database, color: 'text-orange-400' },
          { label: '500-Turn Retention', value: '75%', unit: '', icon: ShieldCheck, color: 'text-emerald-400' },
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

      <ProblemSolutionDemo />

      <section className="py-24 px-6 max-w-7xl mx-auto">
        <AnimatedSection className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-black tracking-tighter mb-4">
            Everything AI Memory Needs
          </h2>
          <p className="text-zinc-500 text-lg font-bold max-w-xl mx-auto">
            A complete cognitive architecture, not just a vector database.
          </p>
        </AnimatedSection>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((f, i) => {
            const colors = colorMap[f.color];
            return (
              <AnimatedSection key={f.title} delay={i * 0.05}>
                <div className="glass-card rounded-[24px] p-6 h-full flex flex-col group">
                  <div className={`w-12 h-12 rounded-2xl border flex items-center justify-center mb-5 ${colors}`}>
                    <f.icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-black tracking-tight mb-2 group-hover:text-cyan-400 transition-colors">{f.title}</h3>
                  <p className="text-sm text-zinc-500 font-bold leading-relaxed flex-1">{f.desc}</p>
                </div>
              </AnimatedSection>
            );
          })}
        </div>
      </section>

      <MemoryLifecycleSection />

      <section className="py-24 px-6">
        <div className="max-w-6xl mx-auto bg-zinc-900/50 rounded-[48px] border border-white/5 p-12 md:p-20 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/5 blur-[120px] rounded-full" />
          <div className="absolute bottom-0 left-0 w-72 h-72 bg-purple-500/5 blur-[100px] rounded-full" />

          <AnimatedSection className="relative z-10">
            <Badge className="mb-8 py-2 px-4 bg-purple-500/10 border-purple-500/20 text-purple-400 rounded-full font-bold">
              THE MULTI-AGENT MOAT
            </Badge>
            <h2 className="text-4xl md:text-5xl font-black tracking-tighter mb-16">
              Bridges the Memory Gap
            </h2>
          </AnimatedSection>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12 relative z-10">
            <AnimatedSection delay={0.1}>
              <div className="flex items-center gap-3 mb-4">
                <Target className="w-6 h-6 text-red-400" />
                <h3 className="text-xl font-black">Problem</h3>
              </div>
              <p className="text-zinc-400 font-bold leading-relaxed">
                Every AI agent today suffers from goldfish memory. Each session starts from zero.
                No learning. No personalization. No continuity.
              </p>
            </AnimatedSection>
            <AnimatedSection delay={0.2}>
              <div className="flex items-center gap-3 mb-4">
                <Layers className="w-6 h-6 text-cyan-400" />
                <h3 className="text-xl font-black">Solution</h3>
              </div>
              <p className="text-zinc-400 font-bold leading-relaxed">
                Recallix is a plug-and-play cognitive memory engine. A universal interop substrate with
                HNSW indexing, hardware-accelerated search, and self-evolving schemas for any AI.
              </p>
            </AnimatedSection>
            <AnimatedSection delay={0.3}>
              <div className="flex items-center gap-3 mb-4">
                <TrendingUp className="w-6 h-6 text-emerald-400" />
                <h3 className="text-xl font-black">Market</h3>
              </div>
              <p className="text-zinc-400 font-bold leading-relaxed">
                Shared memory is the missing link for agent frameworks.
                Recallix becomes the standard substrate for collective AI intelligence.
              </p>
            </AnimatedSection>
          </div>
        </div>
      </section>

      <section className="py-24 px-6 max-w-5xl mx-auto">
        <AnimatedSection className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-black tracking-tighter mb-4">
            Hybrid Architecture
          </h2>
          <p className="text-zinc-500 text-lg font-bold max-w-xl mx-auto">
            Python AI brain for reasoning. C++ infrastructure for performance.
          </p>
        </AnimatedSection>

        <AnimatedSection delay={0.1}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass-card rounded-[28px] p-8">
              <div className="flex items-center gap-3 mb-6">
                <Brain className="w-6 h-6 text-cyan-400" />
                <h3 className="text-xl font-black">Python AI Brain</h3>
              </div>
              <div className="space-y-3">
                {["Memory Manager", "Recall Engine", "Attention Controller", "Model Router (Ollama)", "World Model", "Meta-Memory Optimizer"].map((item) => (
                  <div key={item} className="flex items-center gap-2 text-sm font-bold text-zinc-400">
                    <div className="w-1.5 h-1.5 rounded-full bg-cyan-500" />
                    {item}
                  </div>
                ))}
              </div>
            </div>
            <div className="glass-card rounded-[28px] p-8">
              <div className="flex items-center gap-3 mb-6">
                <Cpu className="w-6 h-6 text-purple-400" />
                <h3 className="text-xl font-black">C++ Infrastructure</h3>
              </div>
              <div className="space-y-3">
                {["HNSW Indexing (Hierarchical)", "NEON SIMD Parallelism", "SQLite WAL Concurrency", "Atomic Timeline Indexing", "Hardware-Aware Cosine Similarity", "Zero-Copy Event Buffering"].map((item) => (
                  <div key={item} className="flex items-center gap-2 text-sm font-bold text-zinc-400">
                    <div className="w-1.5 h-1.5 rounded-full bg-purple-500" />
                    {item}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </AnimatedSection>

        <AnimatedSection delay={0.2} className="mt-8 text-center">
          <Link href="/architecture">
            <Button variant="outline" className="h-12 px-8 border-white/10 rounded-2xl font-bold hover:bg-white/5">
              Explore Full Architecture <ArrowRight className="ml-2 w-4 h-4" />
            </Button>
          </Link>
        </AnimatedSection>
      </section>

      <section className="py-24 px-6 text-center">
        <AnimatedSection>
          <h2 className="text-4xl md:text-6xl font-black tracking-tighter mb-8 max-w-3xl mx-auto leading-tight">
            Give your agents a{" "}
            <span className="text-gradient">memory they deserve.</span>
          </h2>
          <div className="flex flex-wrap gap-4 justify-center relative z-10">
            <Link href="/architecture">
              <Button className="h-14 px-10 bg-cyan-500 hover:bg-cyan-400 text-black font-black text-lg rounded-2xl">
                View Architecture
              </Button>
            </Link>
            <Link href="/benchmark">
              <Button variant="outline" className="h-14 px-10 border-white/10 font-black text-lg rounded-2xl hover:bg-white/5">
                View Performance Audit
              </Button>
            </Link>
            <Link href="https://github.com/AyishikD/Recallix">
              <Button variant="outline" className="h-14 px-10 border-white/10 font-black text-lg rounded-2xl hover:bg-white/5 gap-2">
                <Github className="w-5 h-5" /> GitHub
              </Button>
            </Link>
          </div>
        </AnimatedSection>
      </section>

      <footer className="border-t border-white/5 py-8 px-8 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-zinc-600" />
          <span className="text-xs font-bold text-zinc-600">RECALLIX</span>
        </div>
        <div className="flex items-center gap-6">
          <Link href="https://github.com/AyishikD/Recallix" className="text-xs font-bold text-zinc-600 hover:text-white transition-colors">
            GitHub
          </Link>
          <span className="text-xs text-zinc-700">Persistent Memory Infrastructure for AI Agents</span>
        </div>
      </footer>
    </div>
  );
}
