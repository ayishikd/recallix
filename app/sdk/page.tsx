"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { 
  Terminal, Code2, Cpu, Database, 
  CheckCircle2, Copy, Zap, ArrowRight,
  Shield, Network, Brain, Github, Terminal as TerminalIcon
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";

const pythonCode = `import requests

# 1. Initialize Memory Substrate
BASE_URL = "http://localhost:8000"
headers = {"X-API-Key": "recallix_test_key"}

# 2. Store Cognitive Intent
payload = {
    "agent_id": "researcher_alpha",
    "user_id": "user_123",
    "text": "The project anniversary is December 12th.",
    "importance": 9.5,
    "metadata": {"category": "events"}
}
requests.post(f"{BASE_URL}/memory/store", json=payload, headers=headers)

# 3. Retrieve Context Across Models
query = {"query": "When is the anniversary?", "user_id": "user_123"}
res = requests.post(f"{BASE_URL}/memory/recall", json=query, headers=headers)
print(res.json()["context"])`;

const curlCode = `curl -X POST "http://localhost:8000/memory/store" \\
     -H "X-API-Key: recallix_test_key" \\
     -H "Content-Type: application/json" \\
     -d '{
       "agent_id": "agent_01",
       "user_id": "user_99",
       "text": "User prefers dark mode interfaces.",
       "importance": 7.0
     }'`;

export default function SDKPage() {
  const [copied, setCopied] = useState<string | null>(null);

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

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
          <Link href="/roadmap" className="text-sm font-bold text-zinc-400 hover:text-white transition-colors">Roadmap</Link>
          <Link href="/observability" className="text-sm font-bold text-zinc-400 hover:text-white transition-colors">Observability</Link>
        </div>
        <Link href="https://github.com/AyishikD/Recallix">
           <Button className="h-10 px-5 bg-white text-black font-black rounded-full flex items-center gap-2">
             <Github className="w-4 h-4" /> Star
           </Button>
        </Link>
      </nav>

      <main className="pt-32 pb-24 container mx-auto px-6 max-w-6xl">
        <header className="mb-20">
          <Badge className="mb-6 py-1.5 px-4 bg-cyan-500/10 border-cyan-500/20 text-cyan-400 rounded-full font-bold text-xs">
            DEVELOPER ACCESS
          </Badge>
          <h1 className="text-6xl md:text-7xl font-black tracking-tighter leading-[0.85] mb-8">
            Universal <br />
            <span className="text-gradient">Integrations.</span>
          </h1>
          <p className="text-xl text-zinc-500 font-bold leading-relaxed max-w-2xl">
            Give any agent persistent memory in minutes. Our REST API and SDKs enable 
            seamless context propagation across your entire model stack.
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
          {/* Left Column: Code */}
          <div className="lg:col-span-7 space-y-8">
            <section className="bg-zinc-900/40 border border-white/5 rounded-[32px] p-8 relative overflow-hidden">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <TerminalIcon className="w-5 h-5 text-cyan-400" />
                  <span className="text-sm font-black text-white uppercase tracking-widest">Python Implementation</span>
                </div>
                <button 
                  onClick={() => copyToClipboard(pythonCode, "python")}
                  className="p-2 hover:bg-white/5 rounded-lg transition-colors"
                >
                  {copied === "python" ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4 text-zinc-500" />}
                </button>
              </div>
              <pre className="text-xs md:text-sm font-mono text-cyan-100/80 leading-relaxed overflow-x-auto">
                {pythonCode}
              </pre>
            </section>

            <section className="bg-zinc-900/40 border border-white/5 rounded-[32px] p-8 relative overflow-hidden">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <Code2 className="w-5 h-5 text-purple-400" />
                  <span className="text-sm font-black text-white uppercase tracking-widest">Raw CURL Request</span>
                </div>
                <button 
                  onClick={() => copyToClipboard(curlCode, "curl")}
                  className="p-2 hover:bg-white/5 rounded-lg transition-colors"
                >
                  {copied === "curl" ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4 text-zinc-500" />}
                </button>
              </div>
              <pre className="text-xs md:text-sm font-mono text-purple-100/80 leading-relaxed overflow-x-auto">
                {curlCode}
              </pre>
            </section>
          </div>

          {/* Right Column: Setup */}
          <div className="lg:col-span-5 space-y-6">
            <div className="glass-card rounded-[32px] p-8 border border-white/5">
              <h3 className="text-xl font-black mb-6">Local Environment</h3>
              <div className="space-y-6">
                <div className="flex gap-4">
                  <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center flex-shrink-0">
                    <span className="text-xs font-black text-emerald-400">01</span>
                  </div>
                  <div>
                    <h4 className="text-sm font-black text-white mb-1">Pull Required Models</h4>
                    <p className="text-xs text-zinc-500 font-bold leading-relaxed mb-3">Recallix benchmarks require these exact models locally:</p>
                    <div className="bg-black p-3 rounded-xl border border-white/5 font-mono text-[10px] text-zinc-400 space-y-1">
                       <div>ollama pull llama3.1:8b</div>
                       <div>ollama pull mistral:latest</div>
                       <div>ollama pull mxbai-embed-large</div>
                    </div>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center flex-shrink-0">
                    <span className="text-xs font-black text-blue-400">02</span>
                  </div>
                  <div>
                    <h4 className="text-sm font-black text-white mb-1">Initialize Core</h4>
                    <p className="text-xs text-zinc-500 font-bold leading-relaxed">
                      Clone the substrate, install dependencies, and run the FastAPI entry point.
                    </p>
                    <div className="bg-black p-3 rounded-xl border border-white/5 font-mono text-[10px] text-zinc-400 mt-3">
                       python server.py
                    </div>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center flex-shrink-0">
                    <span className="text-xs font-black text-purple-400">03</span>
                  </div>
                  <div>
                    <h4 className="text-sm font-black text-white mb-1">Scale to Production</h4>
                    <p className="text-xs text-zinc-500 font-bold leading-relaxed">
                      Deploy the C++ VectorEngine for 10M+ node performance.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-cyan-500/5 border border-cyan-500/10 rounded-[32px] p-8">
               <h3 className="text-lg font-black text-cyan-400 mb-2">SDK Roadmap</h3>
               <p className="text-xs text-zinc-500 font-bold leading-relaxed mb-6">
                 We are currently developing official wrappers for TypeScript and Rust.
               </p>
               <Button className="w-full h-12 bg-cyan-500 hover:bg-cyan-400 text-black font-black rounded-xl gap-2">
                 Join the Waitlist <ArrowRight className="w-4 h-4" />
               </Button>
            </div>
          </div>
        </div>
      </main>

      <footer className="border-t border-white/5 py-8 px-8 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-zinc-600" />
          <span className="text-xs font-bold text-zinc-600">RECALLIX SDK</span>
        </div>
        <Link href="https://github.com/AyishikD/Recallix">
           <span className="text-xs text-zinc-700 hover:text-white transition-colors">View Repository</span>
        </Link>
      </footer>
    </div>
  );
}
