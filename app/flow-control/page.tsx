"use client";

import React, { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Brain, Cpu, Database, GitBranch, Layers, ArrowLeft, ChevronRight,
    Workflow, Play, Pause, RotateCcw, Search, BarChart3, RefreshCw,
    Network, Zap, Users, Shield, TrendingUp, Clock, Eye, Lightbulb, ArrowDown, Box, Trash2, Archive, Sparkles, Target, Timer
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";

/* ───────── Type Definitions ───────── */
interface StageInfo {
    id: number;
    title: string;
    subtitle: string;
    detail: string;
    codeSnippet: string;
    icon: React.ReactNode;
    system: "python" | "cpp" | "ollama";
    duration: string;
    dataFlow: string;
}

interface WorkerInfo {
    name: string;
    interval: string;
    icon: React.ReactNode;
    desc: string;
    color: string;
}

/* ───────── Stage Data ───────── */
const STORE_STAGES: StageInfo[] = [
    {
        id: 1, title: "Sensory Buffer", subtitle: "Input Reception",
        detail: "Raw text enters a bounded deque (maxlen=10) with a 60-second TTL. Acts as the ultra-short-term buffer — like human iconic/echoic memory. Expired items are silently discarded on next read.",
        codeSnippet: `self.memories[user_id] = deque(maxlen=10)\nself.memories[user_id].append({\n  "content": message,\n  "timestamp": time.time()\n})`,
        icon: <Eye className="w-5 h-5" />, system: "python", duration: "~0.1ms",
        dataFlow: "Raw text → In-memory deque (per-user)"
    },
    {
        id: 2, title: "Working Memory", subtitle: "Context Assembly",
        detail: "Active conversation context is loaded from working_memory.json, then updated with the new message. This maintains a rolling summary and goal tracking — the AI's 'scratchpad' for current context.",
        codeSnippet: `context = self.working.get(user_id)\nself.working.update(user_id, message)\n# Appends to summary: \" | {message}\"\n# Persists to working_memory.json`,
        icon: <Brain className="w-5 h-5" />, system: "python", duration: "~1ms",
        dataFlow: "Message → JSON file (working_memory.json)"
    },
    {
        id: 3, title: "Importance Scoring", subtitle: "Relevance Analysis",
        detail: "ImportanceRanker calculates a 1-10 score using four factors: Novelty (embedding distance from existing memories), Relevance (keyword overlap with current context), Frequency (repetition signal), and Task Priority (goal/task keyword detection). Score labels: LOW(<4), MEDIUM(4-7), HIGH(7-9), CRITICAL(9+).",
        codeSnippet: `score = novelty * relevance * frequency * priority\n# novelty: 1-3 (embedding distance)\n# relevance: 1-3 (context overlap)\n# frequency: 1-2 (repetition)\n# priority: 1-2 (goal keywords)\nreturn min(max(score, 1.0), 10.0)`,
        icon: <TrendingUp className="w-5 h-5" />, system: "python", duration: "~2ms",
        dataFlow: "Message + Context → Float score [1.0 - 10.0]"
    },
    {
        id: 4, title: "Episodic Storage", subtitle: "Event Recording",
        detail: "The memory event is persisted to SQLite (WAL mode for concurrent reads). Stores: user_id, content, timestamp, importance, reinforcement_score (1.0 default), retrieval_count, cluster_id, and schema_tags. Retries up to 5× on lock contention.",
        codeSnippet: `INSERT INTO episodic_events\n  (user_id, content, timestamp,\n   importance, last_accessed,\n   cluster_id, schema_tags)\nVALUES (?, ?, ?, ?, ?, ?, ?)\n-- PRAGMA journal_mode=WAL`,
        icon: <Database className="w-5 h-5" />, system: "python", duration: "~3ms",
        dataFlow: "Event dict → SQLite (memory.db, WAL mode)"
    },
    {
        id: 5, title: "Vector Engine", subtitle: "Semantic Embedding",
        detail: "A 128-dimensional embedding is generated for the message (mock: normalized random vector; production: sentence-transformer). The vector + metadata is sent via POST /add_vector to the C++ VectorEngine running on port 8080. The cosine similarity index is updated, and the memory is indexed via POST /index_memory.",
        codeSnippet: `vec = np.random.rand(128).astype(float32)\nvec = vec / np.linalg.norm(vec)\n\nPOST :8080/add_vector\n  { "id": "user_ts", "vector": [...] }\nPOST :8080/index_memory\n  { "id": "...", "importance": 7.2 }`,
        icon: <Cpu className="w-5 h-5" />, system: "cpp", duration: "~5ms",
        dataFlow: "Text → 128D vector → C++ VectorEngine (:8080)"
    },
    {
        id: 6, title: "Knowledge Graph", subtitle: "Relational Mapping",
        detail: "A node is added to the knowledge graph via the C++ GraphEngine. This enables relational queries — finding memories connected by shared entities, topics, or temporal proximity. Uses adjacency list storage with BFS/DFS traversal support.",
        codeSnippet: `POST :8080/add_node\n  { "id": message, "type": "event" }\n\n// GraphEngine stores:\n// adjacency_list[id] = neighbors\n// node_types[id] = \"event\"`,
        icon: <Network className="w-5 h-5" />, system: "cpp", duration: "~2ms",
        dataFlow: "Event → C++ GraphEngine node (adjacency list)"
    },
    {
        id: 7, title: "Clustering", subtitle: "Topic Grouping",
        detail: "The C++ ClusteringEngine groups similar memories together using k-means clustering on vector embeddings. Clusters enable rapid topic-based retrieval and help the forgetting system identify which memories are redundant within a cluster.",
        codeSnippet: `POST :8080/cluster\n\n// ClusteringEngine:\n// k-means on embeddings\n// Assigns cluster_id per memory\n// Enables cluster-based retrieval`,
        icon: <Box className="w-5 h-5" />, system: "cpp", duration: "~3ms",
        dataFlow: "Vector embedding → Cluster assignment (cluster_id)"
    },
    {
        id: 8, title: "Schema Tagging", subtitle: "Semantic Classification",
        detail: "Rule-based classification detects schema types from keywords: identity ('name', 'I am'), preference ('allergic', 'prefer', 'hate'), calendar ('meeting', 'schedule', 'deadline'), learning ('learn', 'study', 'course'). Tags influence importance multipliers and meta-memory evolution.",
        codeSnippet: `msg_lower = message.lower()\nif "name" in msg_lower: → "identity"\nif "allergic" in msg:  → "preference"\nif "meeting" in msg:   → "calendar"\nif "learn" in msg:     → "learning"\nelse:                  → "general"`,
        icon: <Layers className="w-5 h-5" />, system: "python", duration: "~0.5ms",
        dataFlow: "Message text → Schema tag array [\"identity\", ...]"
    },
    {
        id: 9, title: "Long-Term Promotion", subtitle: "Importance Gate",
        detail: "If importance > 8.0, the memory is PROMOTED to long-term storage with Ebbinghaus decay protection. Promoted memories are stored in long_term_facts table and protected from the forgetting worker. Sub-threshold memories remain in episodic with a 30-day decay half-life.",
        codeSnippet: `if importance > 8.0:\n  self.long_term.promote(user_id, event)\n  # → INSERT INTO long_term_facts\n  # Protected from forgetting\n  # Ebbinghaus decay model applied\nelse:\n  # Stays in episodic (30d half-life)`,
        icon: <Shield className="w-5 h-5" />, system: "python", duration: "~2ms",
        dataFlow: "High-importance events → long_term_facts (SQLite)"
    },
    {
        id: 10, title: "Timeline Engine", subtitle: "Temporal Sequencing",
        detail: "The event is appended to a chronological timeline via the C++ TimelineEngine. This enables temporal pattern detection — identifying recurring events, trends, and time-based correlations across the user's entire memory history.",
        codeSnippet: `POST :8080/append_event\n  { "user_id": "...",\n    "content": message }\n\n// TimelineEngine stores in SQLite:\n// timeline.db → events table\n// Ordered by timestamp`,
        icon: <Clock className="w-5 h-5" />, system: "cpp", duration: "~2ms",
        dataFlow: "Event → C++ TimelineEngine → timeline.db"
    },
    {
        id: 11, title: "State Inference", subtitle: "LLM Analysis",
        detail: "The event is sent to Llama 3.1:8B via Ollama for latent state inference. The LLM analyzes the interaction to infer hidden user states: skill_level, interest_strength, topic_mastery, emotional_state. Results are persisted to states.db with confidence scores.",
        codeSnippet: `prompt = \"Based on interactions,\n  infer hidden user states...\"\n\nOllama → Llama 3.1:8B\n  → \"skill_level: intermediate\"\n  → \"interest: high\"\n\nINSERT INTO user_states\n  (state_key, state_value, confidence)`,
        icon: <Sparkles className="w-5 h-5" />, system: "ollama", duration: "~800ms",
        dataFlow: "Event → Ollama (Llama 3.1:8B) → states.db"
    },
    {
        id: 12, title: "Pipeline Complete", subtitle: "Summary",
        detail: "All 12 stages complete. The memory is now indexed across 3-4 stores (Sensory, Episodic, Semantic/Vector + optionally Long-Term). Schema tags are recorded. Processing log with per-stage timing is returned to the caller for observability.",
        codeSnippet: `return {\n  "importance": 7.2,\n  "schemas": ["preference"],\n  "promoted": false,\n  "total_ms": 820.5,\n  "processing_log": logs  // 12 entries\n}`,
        icon: <Zap className="w-5 h-5" />, system: "python", duration: "Total",
        dataFlow: "All stores updated → Response with processing_log"
    }
];

const RECALL_STAGES: StageInfo[] = [
    {
        id: 1, title: "Predictive Preload", subtitle: "Context Prediction",
        detail: "PredictiveRecall analyzes query patterns to preload likely-needed context. Uses world model predictions and timeline patterns to anticipate what the user might ask about next.",
        codeSnippet: `prediction = self.predictive\n  .preload_context(user_id, query)\n# Returns predicted topic, context`,
        icon: <Lightbulb className="w-5 h-5" />, system: "python", duration: "~5ms",
        dataFlow: "Query → PredictiveRecall → predicted context"
    },
    {
        id: 2, title: "Candidate Retrieval", subtitle: "Parallel Search",
        detail: "Two parallel searches run: Semantic search (top 50 via cosine similarity on 128D vectors through C++ VectorEngine) and Episodic search (top 50 via keyword matching in SQLite). Results are deduplicated by content.",
        codeSnippet: `semantic = self.semantic.search(\n  user_id, query, top_k=50)\nepisodic = self.episodic.search(\n  user_id, query, limit=50)\n# Deduplicate by content`,
        icon: <Search className="w-5 h-5" />, system: "cpp", duration: "~10ms",
        dataFlow: "Query → Semantic(50) + Episodic(50) → ~100 candidates"
    },
    {
        id: 3, title: "Neural Reranking", subtitle: "Cross-Encoder Scoring",
        detail: "NeuralReranker applies cross-encoder scoring to the ~100 candidates, selecting the top 20 most relevant. Uses TF-IDF based scoring with query-document relevance computation.",
        codeSnippet: `reranked = self.reranker.rerank(\n  query, candidates, top_n=20)\n# Cross-encoder scoring\n# TF-IDF relevance computation`,
        icon: <BarChart3 className="w-5 h-5" />, system: "python", duration: "~15ms",
        dataFlow: "~100 candidates → NeuralReranker → Top 20"
    },
    {
        id: 4, title: "Long-Term + Reflections", subtitle: "Fact Lookup",
        detail: "Directly retrieves promoted long-term facts (with Ebbinghaus decay filtering — only facts with strength > 1.0) and top 3 reflections. These are high-confidence, consolidated memories.",
        codeSnippet: `facts = self.long_term.get(user_id)\n# Applies DecayLogic.strength()\n# Filters: strength > 1.0\nreflections = self.reflective\n  .get_reflections(user_id, limit=3)`,
        icon: <Shield className="w-5 h-5" />, system: "python", duration: "~3ms",
        dataFlow: "User ID → long_term_facts + reflections"
    },
    {
        id: 5, title: "Attention Filtering", subtitle: "Final Selection",
        detail: "AttentionController scores all candidates using: reranker_score × importance × recency × reinforcement × prediction_boost. Weights are loaded from meta-memory policies (memory_policies.json). Returns top-K final memories.",
        codeSnippet: `final = rerank_score\n  * (importance * 0.8)\n  * (recency * 0.6)\n  * reinforcement\n  * prediction_boost\n# Top-K by attention_score`,
        icon: <Target className="w-5 h-5" />, system: "python", duration: "~2ms",
        dataFlow: "Top 20 → AttentionController → Top K final"
    },
    {
        id: 6, title: "Reinforcement Update", subtitle: "Learning Signal",
        detail: "MemoryRL applies positive reinforcement to recalled memories — increasing their reinforcement_score and retrieval_count. This implements a SARSA-like learning signal: memories that get recalled more become easier to recall again.",
        codeSnippet: `for m in final_memories:\n  old = m.reinforcement_score\n  new = rl.reinforce_positive(old)\n  UPDATE episodic_events SET\n    reinforcement_score = new,\n    retrieval_count += 1`,
        icon: <RefreshCw className="w-5 h-5" />, system: "python", duration: "~3ms",
        dataFlow: "Recalled memories → Updated reinforcement scores"
    }
];

const MULTI_AGENT_STORE_STAGES: StageInfo[] = [
    {
        id: 1, title: "Agent Identification", subtitle: "Registry Validation",
        detail: "The system identifies the message source by checking the API key or agent_id against the AgentRegistry SQLite database.",
        codeSnippet: "agent = registry.get_agent(agent_id)\nif not agent:\n    raise AgentNotFoundError()",
        icon: <Users className="w-5 h-5" />, system: "python", duration: "~1ms",
        dataFlow: "AgentID → AgentProfile (name, role, permissions)"
    },
    {
        id: 2, title: "Privacy Validation", subtitle: "Isolation Check",
        detail: "The PrivacyEngine determines if the memory should be sandboxed. PRIVATE memories are only visible to the owner.",
        codeSnippet: "if memory_type == 'private':\n    scope = f'agent_{agent_id}'\nelse:\n    scope = 'global_shared'",
        icon: <Shield className="w-5 h-5" />, system: "python", duration: "~2ms",
        dataFlow: "MemoryType → StorageScope (private | shared)"
    },
    {
        id: 3, title: "Coordination Sync", subtitle: "Multi-Agent Hub",
        detail: "Syncs with the agent specific hub. Multi-threaded C++ coordination layer ensures no data race during concurrent agent stores.",
        codeSnippet: "CoordinationLayer::sync_agent_hub(agent_id, memory_buffer);",
        icon: <Cpu className="w-5 h-5" />, system: "cpp", duration: "~10ms",
        dataFlow: "MemoryBuffer → C++ CoordinationHub"
    },
    {
        id: 4, title: "Shared Routing", subtitle: "Knowledge Broadcast",
        detail: "If SHARED, the AgentRouter identifies subscriber agents who might find this information relevant via proximity matching.",
        codeSnippet: "if scope == 'shared':\n    subscribers = router.find_subscribers(topics)\n    router.broadcast(memory_id, subscribers)",
        icon: <GitBranch className="w-5 h-5" />, system: "python", duration: "~5ms",
        dataFlow: "SharedEvent → BroadcastQueue [AgentB, AgentC...]"
    },
    {
        id: 5, title: "Working Memory", subtitle: "Context Update",
        detail: "Updates the agent's short-term working memory buffer to include the new interaction context.",
        codeSnippet: "working_memory.update(agent_id, msg)\nworking_memory.save()",
        icon: <Layers className="w-5 h-5" />, system: "python", duration: "~1ms",
        dataFlow: "Message → working_memory.json (scoped)"
    },
    {
        id: 6, title: "Persistence Gate", subtitle: "Final Entry",
        detail: "Final storage update. Memories are persisted with explicit ownership tags in both Vector and Graph engines.",
        codeSnippet: "memory.store(msg, agent_id=agent_id)\n# Confirmed in episodic.db with ownership_tag",
        icon: <Database className="w-5 h-5" />, system: "cpp", duration: "~5ms",
        dataFlow: "Event → DB (agent_id: 'assistant_01')"
    }
];

const AME_STAGES: StageInfo[] = [
    {
        id: 1, title: "Topic Clustering", subtitle: "Pattern Detection",
        detail: "The EvolutionWorker runs a DBSCAN clustering algorithm over recent episodic events to find dense semantic patterns.",
        codeSnippet: "clusters = PatternDetector.find_clusters(recent_embeddings)\n# Detected high-density cluster: 'sushi', 'tuna', 'salmon'",
        icon: <Layers className="w-5 h-5" />, system: "python", duration: "~100ms",
        dataFlow: "EpisodicMemories → SemanticClusters"
    },
    {
        id: 2, title: "Schema Proposal", subtitle: "Dynamic Generation",
        detail: "Ollama analyzes the clusters to propose a formal schema ID and required fields for the new conceptual structure.",
        codeSnippet: "propose = llm.generate_schema(cluster)\n# Proposal: { id: 'food_preferences', fields: ['item', 'type'] }",
        icon: <Zap className="w-5 h-5" />, system: "ollama", duration: "~2s",
        dataFlow: "ClusterText → JSON Schema Proposal"
    },
    {
        id: 3, title: "Conflict Resolution", subtitle: "Registry Validation",
        detail: "The SchemaRegistry checks for collisions or near-matches with existing schemas to avoid redundant intelligence structures.",
        codeSnippet: "if registry.exists(proposal.id):\n    # Merge logic or cancel evolution\n    registry.merge(proposal.id)",
        icon: <Shield className="w-5 h-5" />, system: "python", duration: "~5ms",
        dataFlow: "Proposal → SchemaRegistry Match Result"
    },
    {
        id: 4, title: "Memory Migration", subtitle: "Cognitive Relocation",
        detail: "Legacy memories are moved from general episodic storage to the new, highly-efficient conceptual layer.",
        codeSnippet: "MigrationEngine::migrate(memories, to_schema='food_preferences');",
        icon: <Database className="w-5 h-5" />, system: "cpp", duration: "~50ms",
        dataFlow: "RawMemories → StructuredSchemaNodes"
    },
    {
        id: 5, title: "Graph Linkage", subtitle: "World Model Integration",
        detail: "The C++ GraphEngine builds semantic links between the new conceptual schema node and existing high-importance concepts.",
        codeSnippet: "GraphEngine::link_nodes(schema_node_id, global_root_id, weight=0.8);",
        icon: <Network className="w-5 h-5" />, system: "cpp", duration: "~10ms",
        dataFlow: "SchemaNode → GraphRelationshipEdges"
    },
    {
        id: 6, title: "Persistence", subtitle: "Registry Finalization",
        detail: "The new schema is formally registered and becomes available for the RecallEngine's future contextual lookups.",
        codeSnippet: "registry.finalize(schema_id)\n# Successfully evolved 'food_preferences'",
        icon: <Brain className="w-5 h-5" />, system: "python", duration: "~1ms",
        dataFlow: "FinalizedSchema → active_schemas.json"
    }
];

const WORKERS: WorkerInfo[] = [
    { name: "Reflection", interval: "1h", icon: <Lightbulb className="w-4 h-4" />, desc: "Generates high-level insights from recent memories via LLM", color: "from-purple-500 to-violet-600" },
    { name: "Clustering", interval: "2h", icon: <Box className="w-4 h-4" />, desc: "Re-clusters memory vectors via C++ ClusteringEngine", color: "from-orange-500 to-amber-600" },
    { name: "Evolution", interval: "1h", icon: <Zap className="w-4 h-4" />, desc: "AME Engine: Clusters memories to discover new conceptual schemas", color: "from-amber-400 to-orange-600" },
    { name: "Agent Hub", interval: "Sync", icon: <Users className="w-4 h-4" />, desc: "Ensures cross-agent memory isolation and shared registry consistency", color: "from-blue-600 to-indigo-700" },
    { name: "Decay", interval: "4h", icon: <Clock className="w-4 h-4" />, desc: "Compacts decayed memories via C++ infra /compact", color: "from-red-500 to-rose-600" },
    { name: "Compression", interval: "30m", icon: <Archive className="w-4 h-4" />, desc: "LLM summarizes 50-100 raw messages into conversation summaries", color: "from-blue-500 to-cyan-600" },
    { name: "Replay", interval: "6h", icon: <RefreshCw className="w-4 h-4" />, desc: "Sleep-like consolidation — replays and strengthens important memories", color: "from-indigo-500 to-blue-600" },
    { name: "State Inference", interval: "15m", icon: <Sparkles className="w-4 h-4" />, desc: "Llama 3.1:8B infers user hidden states (skill, interest, mastery)", color: "from-emerald-500 to-teal-600" },
    { name: "Prediction", interval: "30m", icon: <Eye className="w-4 h-4" />, desc: "World model predicts user's next likely queries/needs", color: "from-sky-500 to-blue-600" },
    { name: "Ranking", interval: "1h", icon: <TrendingUp className="w-4 h-4" />, desc: "Recalculates importance scores across all episodic memories", color: "from-yellow-500 to-orange-600" },
    { name: "Forgetting", interval: "24h", icon: <Trash2 className="w-4 h-4" />, desc: "RL-based cleanup: delete/archive/protect decisions per memory", color: "from-rose-500 to-red-600" },
    { name: "Meta-Analysis", interval: "12h", icon: <BarChart3 className="w-4 h-4" />, desc: "Analyzes memory system performance and optimizes policies", color: "from-fuchsia-500 to-pink-600" },
];

const systemColors = {
    python: { bg: "bg-blue-500/20", text: "text-blue-400", border: "border-blue-500/30", glow: "shadow-blue-500/20" },
    cpp: { bg: "bg-orange-500/20", text: "text-orange-400", border: "border-orange-500/30", glow: "shadow-orange-500/20" },
    ollama: { bg: "bg-purple-500/20", text: "text-purple-400", border: "border-purple-500/30", glow: "shadow-purple-500/20" },
};

/* ───────── Components ───────── */

function DataParticle({ active, delay = 0 }: { active: boolean; delay?: number }) {
    if (!active) return null;
    return (
        <motion.div
            className="absolute left-1/2 -translate-x-1/2 w-2 h-2 rounded-full bg-cyan-400 shadow-lg shadow-cyan-400/50"
            initial={{ top: -8, opacity: 0, scale: 0 }}
            animate={{ top: 40, opacity: [0, 1, 1, 0], scale: [0.5, 1, 1, 0.5] }}
            transition={{ duration: 0.8, delay, ease: "easeInOut" }}
        />
    );
}

function StageNode({ stage, index, isActive, isCompleted, isExpanded, onClick, totalStages }: {
    stage: StageInfo; index: number; isActive: boolean; isCompleted: boolean;
    isExpanded: boolean; onClick: () => void; totalStages: number;
}) {
    const sc = systemColors[stage.system];
    return (
        <div className="relative">
            {/* Connector line */}
            {index < totalStages - 1 && (
                <div className="absolute left-8 top-full w-0.5 h-8 z-0">
                    <motion.div
                        className="w-full h-full bg-gradient-to-b from-cyan-500/50 to-transparent"
                        initial={{ scaleY: 0 }}
                        animate={{ scaleY: isCompleted ? 1 : 0.3, opacity: isCompleted ? 1 : 0.2 }}
                        transition={{ duration: 0.4 }}
                    />
                    <DataParticle active={isActive} />
                </div>
            )}

            <motion.div
                layout
                onClick={onClick}
                className={`relative cursor-pointer rounded-2xl border p-5 transition-all duration-300
          ${isActive ? `${sc.border} bg-gradient-to-r ${sc.bg} shadow-lg ${sc.glow}` :
                        isCompleted ? "border-zinc-700/50 bg-zinc-900/40" : "border-zinc-800/30 bg-zinc-950/30"}`}
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.06, duration: 0.4 }}
                whileHover={{ scale: 1.01, borderColor: "rgba(34,211,238,0.3)" }}
            >
                <div className="flex items-start gap-4">
                    {/* Stage number circle */}
                    <motion.div
                        className={`relative flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center text-sm font-bold
              ${isActive ? `bg-gradient-to-br ${sc.bg} ${sc.text} ring-2 ring-cyan-400/30` :
                                isCompleted ? "bg-emerald-500/20 text-emerald-400" : "bg-zinc-800/50 text-zinc-500"}`}
                        animate={isActive ? { scale: [1, 1.1, 1] } : {}}
                        transition={{ duration: 1.5, repeat: Infinity }}
                    >
                        {isCompleted ? "✓" : stage.id}
                        {isActive && (
                            <motion.div
                                className="absolute inset-0 rounded-xl border-2 border-cyan-400/40"
                                animate={{ scale: [1, 1.4], opacity: [0.6, 0] }}
                                transition={{ duration: 1.5, repeat: Infinity }}
                            />
                        )}
                    </motion.div>

                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-1 flex-wrap">
                            <h3 className={`font-semibold text-base ${isActive ? "text-white" : isCompleted ? "text-zinc-300" : "text-zinc-500"}`}>
                                {stage.title}
                            </h3>
                            <Badge className={`text-[10px] px-2 py-0 ${sc.bg} ${sc.text} border ${sc.border}`}>
                                {stage.system.toUpperCase()}
                            </Badge>
                            <span className="text-[11px] text-zinc-500 font-mono">{stage.duration}</span>
                            {isActive && (
                                <motion.span
                                    className="text-[10px] text-cyan-400 font-mono"
                                    animate={{ opacity: [1, 0.4, 1] }}
                                    transition={{ duration: 1, repeat: Infinity }}
                                >● PROCESSING</motion.span>
                            )}
                        </div>
                        <p className={`text-sm ${isActive ? "text-zinc-300" : "text-zinc-500"}`}>{stage.subtitle}</p>

                        {/* Data flow indicator */}
                        {(isActive || isCompleted) && (
                            <motion.div
                                className="mt-2 flex items-center gap-2 text-[11px] text-cyan-400/70 font-mono"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                            >
                                <ArrowDown className="w-3 h-3" />
                                {stage.dataFlow}
                            </motion.div>
                        )}
                    </div>

                    <ChevronRight className={`w-4 h-4 text-zinc-600 transition-transform ${isExpanded ? "rotate-90" : ""}`} />
                </div>

                {/* Expanded Detail */}
                <AnimatePresence>
                    {isExpanded && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: "auto", opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.3 }}
                            className="overflow-hidden"
                        >
                            <div className="mt-4 pt-4 border-t border-zinc-800/50 space-y-3">
                                <p className="text-sm text-zinc-400 leading-relaxed">{stage.detail}</p>
                                <div className="rounded-xl bg-black/60 border border-zinc-800/50 p-4 font-mono text-xs text-emerald-400/90 overflow-x-auto">
                                    <pre className="whitespace-pre">{stage.codeSnippet}</pre>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.div>
        </div>
    );
}

function WorkerCard({ worker, index }: { worker: WorkerInfo; index: number }) {
    const [pulse, setPulse] = useState(false);
    useEffect(() => {
        const interval = setInterval(() => {
            setPulse(true);
            setTimeout(() => setPulse(false), 1500);
        }, 3000 + index * 800);
        return () => clearInterval(interval);
    }, [index]);

    return (
        <motion.div
            className="glass-card rounded-xl p-4 relative overflow-hidden group"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.08 }}
            whileHover={{ scale: 1.03, borderColor: "rgba(34,211,238,0.3)" }}
        >
            {pulse && (
                <motion.div
                    className={`absolute inset-0 bg-gradient-to-r ${worker.color} opacity-10`}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: [0, 0.15, 0] }}
                    transition={{ duration: 1.5 }}
                />
            )}
            <div className="flex items-center gap-3 mb-2">
                <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${worker.color} flex items-center justify-center`}>
                    {worker.icon}
                </div>
                <div>
                    <h4 className="text-sm font-semibold text-white">{worker.name}</h4>
                    <span className="text-[10px] font-mono text-zinc-500">every {worker.interval}</span>
                </div>
                <motion.div
                    className="ml-auto w-2 h-2 rounded-full"
                    animate={{
                        backgroundColor: pulse ? "#22d3ee" : "#3f3f46",
                        boxShadow: pulse ? "0 0 8px rgba(34,211,238,0.5)" : "none"
                    }}
                />
            </div>
            <p className="text-xs text-zinc-500 leading-relaxed">{worker.desc}</p>
        </motion.div>
    );
}

/* ───────── Main Page ───────── */
export default function FlowControlPage() {
    const [activeTab, setActiveTab] = useState<"store" | "recall" | "multi" | "ame" | "workers">("store");
    const [activeStage, setActiveStage] = useState(-1);
    const [expandedStage, setExpandedStage] = useState<number | null>(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [completedStages, setCompletedStages] = useState<Set<number>>(new Set());
    const [inputText, setInputText] = useState("I'm allergic to peanuts and prefer dark chocolate");
    const [typedText, setTypedText] = useState("");

    const stages =
        activeTab === "store" ? STORE_STAGES :
            activeTab === "recall" ? RECALL_STAGES :
                activeTab === "multi" ? MULTI_AGENT_STORE_STAGES :
                    AME_STAGES;

    const reset = useCallback(() => {
        setActiveStage(-1);
        setCompletedStages(new Set());
        setIsPlaying(false);
        setTypedText("");
        setExpandedStage(null);
    }, []);

    // Typing animation
    useEffect(() => {
        if (!isPlaying || activeStage !== 0) return;
        let i = 0;
        setTypedText("");
        const interval = setInterval(() => {
            if (i < inputText.length) { setTypedText(inputText.slice(0, i + 1)); i++; }
            else clearInterval(interval);
        }, 40);
        return () => clearInterval(interval);
    }, [isPlaying, activeStage, inputText]);

    // Auto-play
    useEffect(() => {
        if (!isPlaying) return;
        if (activeStage >= stages.length - 1) { setIsPlaying(false); return; }
        const timer = setTimeout(() => {
            setCompletedStages(prev => new Set([...prev, activeStage]));
            setActiveStage(prev => prev + 1);
        }, activeStage === -1 ? 500 : activeStage === 0 ? 2000 : 1200);
        return () => clearTimeout(timer);
    }, [isPlaying, activeStage, stages.length]);

    const startPlayback = () => {
        reset();
        setTimeout(() => { setIsPlaying(true); setActiveStage(0); }, 100);
    };

    return (
        <div className="min-h-screen bg-black text-white relative overflow-hidden">
            {/* Background effects */}
            <div className="fixed inset-0 pointer-events-none">
                <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-cyan-500/5 rounded-full blur-[120px]" />
                <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-purple-500/5 rounded-full blur-[120px]" />
            </div>

            <div className="relative z-10 max-w-5xl mx-auto px-6 py-8">
                {/* Header */}
                <div className="flex items-center gap-4 mb-8">
                    <Link href="/">
                        <Button variant="ghost" size="sm" className="text-zinc-400 hover:text-white gap-2">
                            <ArrowLeft className="w-4 h-4" /> Back
                        </Button>
                    </Link>
                    <div className="h-6 w-px bg-zinc-800" />
                    <div>
                        <h1 className="text-2xl font-bold text-gradient flex items-center gap-3">
                            <Workflow className="w-6 h-6 text-cyan-400" />
                            Flow Control
                        </h1>
                        <p className="text-sm text-zinc-500 mt-1">Complete memory pipeline — stage by stage</p>
                    </div>
                </div>

                {/* Tab Navigation */}
                <div className="flex flex-wrap gap-2 mb-6">
                    {([
                        { key: "store" as const, label: "Single Store", icon: <Database className="w-4 h-4" />, count: "11 stages" },
                        { key: "recall" as const, label: "Single Recall", icon: <Search className="w-4 h-4" />, count: "5 stages" },
                        { key: "multi" as const, label: "Multi-Agent Hub", icon: <Users className="w-4 h-4" />, count: "6 stages" },
                        { key: "ame" as const, label: "AME Evolution", icon: <Zap className="w-4 h-4" />, count: "6 stages" },
                        { key: "workers" as const, label: "Workers", icon: <RefreshCw className="w-4 h-4" />, count: "10 threads" },
                    ]).map(tab => (
                        <button
                            key={tab.key}
                            onClick={() => { setActiveTab(tab.key); reset(); }}
                            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-black uppercase tracking-tight transition-all
                ${activeTab === tab.key
                                    ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-lg shadow-cyan-500/5"
                                    : "text-zinc-500 hover:text-zinc-300 border border-white/5 hover:border-zinc-700 hover:bg-zinc-900/40"}`}
                        >
                            {tab.icon} {tab.label}
                            <span className="text-[10px] font-mono opacity-60 ml-1">{tab.count}</span>
                        </button>
                    ))}
                </div>

                {/* Store / Recall Pipeline */}
                {activeTab !== "workers" && (
                    <>
                        {/* Input simulation bar */}
                        <motion.div
                            className="glass-card rounded-2xl p-5 mb-6"
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                        >
                            <div className="flex items-center gap-4 mb-3">
                                <div className="flex items-center gap-2">
                                    <Play className="w-4 h-4 text-cyan-400" />
                                    <span className="text-sm font-medium text-zinc-300">
                                        {activeTab === "store" ? "Simulate Memory Store" : "Simulate Memory Recall"}
                                    </span>
                                </div>
                                <div className="flex gap-2 ml-auto">
                                    <Button
                                        size="sm"
                                        onClick={startPlayback}
                                        disabled={isPlaying}
                                        className="bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30 border border-cyan-500/30 gap-1.5 text-xs"
                                    >
                                        <Play className="w-3 h-3" /> Auto-Play
                                    </Button>
                                    <Button
                                        size="sm"
                                        onClick={() => setIsPlaying(false)}
                                        disabled={!isPlaying}
                                        className="bg-zinc-800/50 text-zinc-400 hover:bg-zinc-700/50 border border-zinc-700/30 gap-1.5 text-xs"
                                    >
                                        <Pause className="w-3 h-3" /> Pause
                                    </Button>
                                    <Button
                                        size="sm"
                                        onClick={reset}
                                        className="bg-zinc-800/50 text-zinc-400 hover:bg-zinc-700/50 border border-zinc-700/30 gap-1.5 text-xs"
                                    >
                                        <RotateCcw className="w-3 h-3" /> Reset
                                    </Button>
                                </div>
                            </div>

                            {/* Input / typing display */}
                            <div className="rounded-xl bg-black/60 border border-zinc-800/50 p-3 font-mono text-sm">
                                <span className="text-zinc-500">
                                    {activeTab === "store" ? "POST /memory/store → " :
                                        activeTab === "recall" ? "POST /memory/recall → " :
                                            activeTab === "multi" ? "POST /agents/store → " :
                                                "WORKER /ame/evolve → "}
                                </span>
                                <span className="text-cyan-400">
                                    {isPlaying && activeStage >= 0 ? (typedText || inputText) :
                                        activeTab === "ame" ? "ANALYZING RECENT EPISODES..." : inputText}
                                </span>
                                {isPlaying && activeStage === 0 && (
                                    <motion.span
                                        className="text-cyan-400"
                                        animate={{ opacity: [1, 0] }}
                                        transition={{ duration: 0.5, repeat: Infinity }}
                                    >▊</motion.span>
                                )}
                            </div>

                            {/* Progress bar */}
                            {activeStage >= 0 && (
                                <div className="mt-3 h-1 bg-zinc-800/50 rounded-full overflow-hidden">
                                    <motion.div
                                        className="h-full bg-gradient-to-r from-cyan-500 to-purple-500 rounded-full"
                                        initial={{ width: "0%" }}
                                        animate={{ width: `${((completedStages.size + (isPlaying ? 0.5 : 0)) / stages.length) * 100}%` }}
                                        transition={{ duration: 0.4 }}
                                    />
                                </div>
                            )}
                        </motion.div>

                        {/* Pipeline stages */}
                        <div className="space-y-3">
                            {stages.map((stage, i) => (
                                <StageNode
                                    key={stage.id}
                                    stage={stage}
                                    index={i}
                                    isActive={activeStage === i}
                                    isCompleted={completedStages.has(i)}
                                    isExpanded={expandedStage === i}
                                    onClick={() => setExpandedStage(expandedStage === i ? null : i)}
                                    totalStages={stages.length}
                                />
                            ))}
                        </div>

                        {/* Completion summary */}
                        <AnimatePresence>
                            {completedStages.size === stages.length && (
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="mt-6 glass-card rounded-2xl p-6 border-emerald-500/30"
                                >
                                    <div className="flex items-center gap-3 mb-3">
                                        <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center">
                                            <Zap className="w-5 h-5 text-emerald-400" />
                                        </div>
                                        <div>
                                            <h3 className="font-semibold text-emerald-400">Pipeline Complete</h3>
                                            <p className="text-xs text-zinc-500">All {stages.length} stages processed successfully</p>
                                        </div>
                                    </div>
                                    {(activeTab === "store" || activeTab === "multi" || activeTab === "ame") && (
                                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4">
                                            {(activeTab === "store" ? [
                                                { label: "Stores Updated", value: "4", color: "text-cyan-400" },
                                                { label: "Schema Tags", value: "preference", color: "text-purple-400" },
                                                { label: "Importance", value: "6.0", color: "text-yellow-400" },
                                                { label: "Promoted", value: "No", color: "text-zinc-400" },
                                            ] : activeTab === "multi" ? [
                                                { label: "Owner Agent", value: "Assistant_01", color: "text-cyan-400" },
                                                { label: "Privacy Scope", value: "Private", color: "text-emerald-400" },
                                                { label: "Registry", value: "Verified", color: "text-blue-400" },
                                                { label: "Shared", value: "Blocked", color: "text-red-400" },
                                            ] : [
                                                { label: "Clusters", value: "x3 Found", color: "text-emerald-400" },
                                                { label: "Schema Proposed", value: "food_prefs", color: "text-purple-400" },
                                                { label: "Migrated", value: "12 Events", color: "text-amber-400" },
                                                { label: "Registry", value: "Updated", color: "text-cyan-400" },
                                            ]).map(s => (
                                                <div key={s.label} className="bg-black/40 border border-white/5 rounded-lg p-3 text-center">
                                                    <p className={`text-lg font-black uppercase tracking-tighter ${s.color}`}>{s.value}</p>
                                                    <p className="text-[10px] font-black uppercase tracking-widest text-zinc-500 mt-1">{s.label}</p>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </>
                )}

                {/* Workers tab */}
                {activeTab === "workers" && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="space-y-6"
                    >
                        <div className="glass-card rounded-2xl p-5 mb-4">
                            <h3 className="text-sm font-semibold text-zinc-300 mb-2 flex items-center gap-2">
                                <RefreshCw className="w-4 h-4 text-cyan-400" />
                                10 Background Daemon Threads
                            </h3>
                            <p className="text-xs text-zinc-500">
                                These workers run independently on background threads, performing maintenance tasks like memory decay, consolidation, clustering, and meta-analysis. They start automatically on server boot via <code className="text-cyan-400/80">BackgroundWorker.start()</code>.
                            </p>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            {WORKERS.map((w, i) => (<WorkerCard key={w.name} worker={w} index={i} />))}
                        </div>

                        {/* Architecture diagram */}
                        <motion.div
                            className="glass-card rounded-2xl p-6 mt-4"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.5 }}
                        >
                            <h3 className="text-sm font-semibold text-zinc-300 mb-4">Worker Lifecycle</h3>
                            <div className="font-mono text-xs text-zinc-500 space-y-1">
                                <p><span className="text-cyan-400">server.py</span> → BackgroundWorker(memory_manager)</p>
                                <p className="pl-4">↳ <span className="text-emerald-400">worker.start()</span></p>
                                <p className="pl-8">↳ 10× <span className="text-purple-400">threading.Thread</span>(target=_run_*, daemon=True).start()</p>
                                <p className="pl-12">↳ Each thread: <span className="text-yellow-400">while self.running:</span> do_work() → sleep(interval)</p>
                            </div>
                        </motion.div>
                    </motion.div>
                )}

                {/* Footer legend */}
                <div className="mt-10 flex items-center justify-center gap-6 text-[11px] text-zinc-600">
                    <div className="flex items-center gap-1.5">
                        <div className="w-2.5 h-2.5 rounded-sm bg-blue-500/40" />
                        <span>Python</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                        <div className="w-2.5 h-2.5 rounded-sm bg-orange-500/40" />
                        <span>C++ Infra</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                        <div className="w-2.5 h-2.5 rounded-sm bg-purple-500/40" />
                        <span>Ollama / LLM</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
