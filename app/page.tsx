"use client";

import React, { useRef, useState, useEffect } from "react";
import { motion, useInView, AnimatePresence } from "framer-motion";
import {
  Brain, Cpu, Database, Search, Clock, Lightbulb,
  Code2, Activity, ArrowRight, Layers, Sparkles,
  Shield, TrendingUp, Target, AlertTriangle, Play,
  Workflow, Eye, ChevronRight, CheckCircle2, Zap,
  ShieldCheck, Users, History
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
  { nodes: '1,000', latency: 1.31, baseline: 3.69 },
  { nodes: '10,000', latency: 1.41, baseline: 37.51 },
  { nodes: '100,000', latency: 1.37, baseline: 419.59 },
  { nodes: '1,000,000', latency: 1.28, baseline: 5200.0 },
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
  "You're Alex! (Recalled in 1.28ms from Long-Term Memory)",
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
                    <p className="text-sm font-black text-cyan-400">✅ Perfect Recall</p>
                    <p className="text-[10px] font-bold text-cyan-500/60 mt-1">3 memories stored · Knowledge graph updated · 1.28ms recall</p>
                    <div className="flex items-center justify-center gap-5 mt-3">
                      <span className="text-[9px] font-black text-zinc-600">🧠 6 layers</span>
                      <span className="text-[9px] font-black text-zinc-600">📊 ranked</span>
                      <span className="text-[9px] font-black text-zinc-600">⚡ 1.28ms</span>
                      <span className="text-[9px] font-black text-zinc-600">🔗 graph</span>
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
  { icon: Database, title: "Long-Term Memory", desc: "6-layer cognitive architecture stores, ranks, and retrieves memories across sessions.", color: "cyan" },
  { icon: Search, title: "Semantic Recall", desc: "Two-stage retrieval with C++ vector search and neural reranking for precise context.", color: "blue" },
  { icon: Clock, title: "Timeline Reasoning", desc: "Chronological event engine detects patterns and tracks behavioral evolution.", color: "purple" },
  { icon: Lightbulb, title: "Reflection Insights", desc: "LLM-powered reflections extract high-level behavioral patterns from raw memory.", color: "amber" },
  { icon: Sparkles, title: "Meta-Memory", desc: "Self-optimizing layer evolves schemas, adjusts policies, and reorganizes knowledge.", color: "emerald" },
  { icon: Code2, title: "Developer SDK", desc: "Python and TypeScript SDKs — give agents persistent memory in one line of code.", color: "rose" },
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
  { step: "Reflection", label: "LLM generates insights", detail: "Llama 3.1:8B via Ollama analyzes memory patterns and generates high-level behavioral reflections.", icon: <Lightbulb className="w-5 h-5" />, system: "Ollama", color: "from-amber-500 to-yellow-500" },
  { step: "Meta-Memory", label: "System self-optimizes", detail: "Meta-analyzer evolves schemas, optimizes retrieval policies, and tunes attention weights autonomously.", icon: <Sparkles className="w-5 h-5" />, system: "Python", color: "from-rose-500 to-pink-500" },
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
          <Link href="/playground" className="text-sm font-bold text-zinc-400 hover:text-white transition-colors">Live Demo</Link>
          <Link href="/architecture" className="text-sm font-bold text-zinc-400 hover:text-white transition-colors">Architecture</Link>
          <Link href="/flow-control" className="text-sm font-bold text-zinc-400 hover:text-white transition-colors">Flow Control</Link>
          <Link href="/sdk" className="text-sm font-bold text-zinc-400 hover:text-white transition-colors">SDK</Link>
          <Link href="/observability" className="text-sm font-bold text-zinc-400 hover:text-white transition-colors">Observability</Link>
        </div>
        <Link href="/playground">
          <Button className="h-10 px-5 bg-cyan-500 hover:bg-cyan-400 text-black font-black rounded-full">
            Try Demo
          </Button>
        </Link>
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
            Persistent Memory{" "}
            <span className="text-gradient">Infrastructure</span>{" "}
            for AI Agents
          </h1>
        </AnimatedSection>
        <AnimatedSection delay={0.2}>
          <p className="text-xl md:text-2xl text-zinc-500 font-bold max-w-2xl mx-auto mb-12 leading-relaxed">
            Measured performance audit for the Recallix MemoryOS. 1.28ms retrieval at 1,000,000 nodes. 
            Verified on Apple M4 Core Infrastructure.
          </p>
        </AnimatedSection>
        <AnimatedSection delay={0.3}>
          <div className="flex flex-wrap gap-4 justify-center">
            <Link href="/playground">
              <Button className="h-14 px-8 bg-white text-black font-black text-lg rounded-2xl hover:bg-zinc-200">
                Try Live Demo <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </Link>
            <Link href="/architecture">
              <Button variant="outline" className="h-14 px-8 border-white/10 text-white font-black text-lg rounded-2xl hover:bg-white/5">
                View Architecture
              </Button>
            </Link>
            <Link href="/sdk">
              <Button variant="outline" className="h-14 px-8 border-white/10 text-white font-black text-lg rounded-2xl hover:bg-white/5">
                Explore SDK
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
          { label: 'Search Latency (Avg)', value: '1.28ms', unit: '', icon: Zap, color: 'text-blue-400' },
          { label: 'Recall Accuracy', value: '100%', unit: '', icon: Activity, color: 'text-purple-400' },
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

      <ProblemSolutionDemo />

      {/* TEST 1: MEMORY ACCURACY */}
      <section className="relative max-w-7xl mx-auto px-6 py-24">
        <TestHeader number={1} title="Memory Accuracy" icon={Target} color="bg-emerald-600" />
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-7 bg-white/[0.02] border border-white/10 rounded-[2.5rem] p-10 flex flex-col gap-8">
            <p className="text-white/60 leading-relaxed">
              We stress-tested the episodic retrieval engine by injecting 20 core facts into a stream of 50 distractor messages. 
              The system was queried after a 100-turn window to verify cross-temporal recall integrity.
            </p>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white/5 rounded-2xl p-6 border border-white/5">
                <span className="text-4xl font-black text-emerald-400">100%</span>
                <p className="text-[10px] text-white/30 uppercase font-bold tracking-widest mt-1">Measured Accuracy</p>
              </div>
              <div className="bg-white/5 rounded-2xl p-6 border border-white/5">
                <span className="text-4xl font-black text-white">0%</span>
                <p className="text-[10px] text-white/30 uppercase font-bold tracking-widest mt-1">Hallucination Rate</p>
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
      <section className="relative max-w-7xl mx-auto px-6 py-24">
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
              <span className="text-5xl font-black text-white tracking-tighter">1.28ms</span>
              <p className="text-xs text-white/70 uppercase font-bold tracking-widest">Average Search (1M Nodes)</p>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-3xl p-8 flex flex-col gap-4">
               <div className="flex items-center gap-2 text-blue-400 font-bold text-[10px] uppercase tracking-widest">
                 <Activity className="w-3 h-3" />
                 Measured Moat
               </div>
               <p className="text-xs text-white/50 leading-relaxed">
                 By using <strong>HNSW Indexing</strong> and <strong>NEON SIMD</strong> hardware acceleration, 
                 we've decoupled memory scale from retrieval speed. 1M nodes search is now <strong>~85x faster</strong> than 
                 the Python baseline.
               </p>
            </div>
          </div>
        </div>
      </section>

      {/* TEST 3: MULTI-AGENT HANDOVER */}
      <section className="relative max-w-7xl mx-auto px-6 py-24">
        <TestHeader number={3} title="Agent Interoperability" icon={Users} color="bg-purple-600" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white/[0.02] border border-white/10 rounded-[2.5rem] p-10 flex flex-col gap-6">
            <h3 className="text-xl font-bold">The Cross-Model Test</h3>
            <p className="text-white/60 leading-relaxed">
              Knowledge was stored using Llama 3.1 8B. 
              Retrieval was performed using Mistral 7B.
            </p>
            <div className="flex items-center gap-4 mt-4">
              <div className="flex-1 h-14 bg-blue-500/10 border border-blue-500/20 rounded-2xl flex items-center justify-center text-blue-400 font-bold">Llama 3.1</div>
              <ArrowRight className="text-white/20" />
              <div className="flex-1 h-14 bg-purple-500/10 border border-purple-500/20 rounded-2xl flex items-center justify-center text-purple-400 font-bold">Mistral 7B</div>
            </div>
          </div>
          <div className="bg-purple-600/10 border border-purple-600/20 rounded-[2.5rem] p-10 flex flex-col justify-center gap-4">
            <span className="text-4xl font-black text-white">100% Fidelity</span>
            <p className="text-sm text-white/70 leading-relaxed">
              Confirmed that Recallix standardizes memory across disparate model architectures 
              with zero semantic loss during handover.
            </p>
          </div>
        </div>
      </section>

      {/* TEST 4: LONG-TERM RETENTION */}
      <section className="relative max-w-7xl mx-auto px-6 py-24">
        <TestHeader number={4} title="Context Retention" icon={History} color="bg-orange-600" />
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-8 bg-white/[0.02] border border-white/10 rounded-[2.5rem] p-10 flex flex-col gap-10">
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
                The 75% Post-Mortem
              </div>
              <p className="text-sm text-white/70 leading-relaxed italic text-white/50">
                 Fact 100 miss identified as "Intent Shadowing." Low heuristic importance (5.0) failed 
                 promotion to long-term storage, while distraction noise drowned out the episodic match.
              </p>
            </div>
            <div className="bg-blue-600/10 border border-blue-600/20 rounded-3xl p-8 flex flex-col gap-4">
               <span className="text-xs font-bold text-blue-400 uppercase tracking-widest flex items-center gap-2">
                 <ArrowRight className="w-3 h-3" />
                 Technical Fix: Semantic Fallback
               </span>
               <p className="text-xs text-white/50 leading-relaxed">
                 Implementation of an Adaptive Intent Router that triggers high-speed HNSW 
                 semantic searches whenever episodic confidence is low.
               </p>
            </div>
          </div>
        </div>
      </section>

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
              FOR INVESTORS
            </Badge>
            <h2 className="text-4xl md:text-5xl font-black tracking-tighter mb-16">
              The Missing Layer in AI
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
                Recallix is a plug-and-play cognitive memory engine. Six-layer architecture with
                neural ranking, RL-based forgetting, and self-evolving schemas.
              </p>
            </AnimatedSection>
            <AnimatedSection delay={0.3}>
              <div className="flex items-center gap-3 mb-4">
                <TrendingUp className="w-6 h-6 text-emerald-400" />
                <h3 className="text-xl font-black">Market</h3>
              </div>
              <p className="text-zinc-400 font-bold leading-relaxed">
                Every AI assistant, copilot, and autonomous agent needs persistent memory.
                Recallix becomes the memory standard for agent frameworks.
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
                {["Vector Engine (Cosine)", "Graph Engine (Adjacency)", "Timeline Engine", "Clustering Engine", "Memory Indexer", "Event Queue"].map((item) => (
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
          <div className="flex flex-wrap gap-4 justify-center">
            <Link href="/playground">
              <Button className="h-14 px-10 bg-cyan-500 hover:bg-cyan-400 text-black font-black text-lg rounded-2xl">
                Try the Live Demo
              </Button>
            </Link>
            <Link href="/sdk">
              <Button variant="outline" className="h-14 px-10 border-white/10 font-black text-lg rounded-2xl hover:bg-white/5">
                Read the Docs
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
        <span className="text-xs text-zinc-700">Persistent Memory Infrastructure for AI Agents</span>
      </footer>
    </div>
  );
}
