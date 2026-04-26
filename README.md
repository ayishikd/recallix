# Recallix - Hardware-Accelerated Cognitive Memory for AI Agents

Every AI agent today is amnesiac. It forgets everything between sessions. Multi-agent systems have no shared memory substrate. We built **Recallix** to fix that — a hardware-accelerated cognitive memory layer that any agent can read from and write to, regardless of which LLM is running underneath.

## 🚀 0.63ms. 1,000,000 nodes. One machine.

| Phase | Test Description | Result | Status |
| :--- | :--- | :--- | :--- |
| **01** | **Fact Recall Accuracy** | **100.0%** (20/20) | ✅ Verified |
| **02** | **1M Node Search (Avg)** | **0.63 ms** | ✅ Measured |
| **02** | **1M Node Search (P99)** | **1.04 ms** | ✅ Measured |
| **03** | **Multi-Agent Handover** | **100% Fidelity** | ✅ Validated |
| **04** | **500-Turn Retention** | **83.3%** | ✅ Analyzed |
| **Scale**| **Speedup vs Python** | **~8,000x** | ✅ Validated |
| **Build**| **1M Index Construction** | **128.01s** | ✅ Measured |

![Recallix Benchmark Dashboard](./dashboard.png)

---

## 💎 Why Recallix Exists
Most RAG systems today are built for documents, not for active agent cognition. They are slow, stateless, and fail at scale. Recallix provides a persistent "Long-Term Memory" layer that allows agents to:
- **Remember** previous user preferences across thousands of turns.
- **Hand over** complex task context to other agents seamlessly.
- **Retrieve** critical facts in sub-millisecond time, ensuring no interruption in agentic thought.

---

## 🛠️ Key Technological Moats

### 1. The HNSW + NEON Core
Recallix bypasses the O(N) linear scan bottleneck by implementing a **Hierarchical Navigable Small World (HNSW)** graph in C++. Every distance calculation is vectorized using **ARM NEON SIMD** intrinsics, allowing for near-instant retrieval even as memory scale approaches millions of nodes.

### 2. Multi-Tiered Cognitive Architecture
Recallix doesn't just store vectors; it manages memory tiers:
- **Episodic Buffer**: Instant recall of recent interactions (SQLite-backed).
- **Cognitive Index (HNSW)**: Logarithmic search over millions of historical facts.
- **Clustering Engine**: Grouping related memories for high-level semantic synthesis.

### 3. Long-Term Retention (Test Phase 04)
In a rigorous 500-turn simulation, Recallix maintained a 100% recall rate for 417 turns, with an overall retention of **83.3%**. 
- **Failure Mode Identified**: "Intent Shadowing" — where deep episodic memories were overshadowed by recent conversational noise.
- **The Solution**: An Adaptive Intent Router that triggers high-speed HNSW semantic searches when episodic confidence is low.

---

## 🏗️ Getting Started

### 1. Build the C++ Infrastructure
```bash
cd backend/infra_cpp
mkdir build && cd build
cmake ..
make -j$(sysctl -n hw.ncpu)
./memory_service
```

### 2. Initialize the Python Brain
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python server.py
```

### 3. Launch the Dashboard
```bash
npm install
npm run dev
```
Visit `http://localhost:3000/benchmark` to view the live performance audit.

---

## 📜 License
MIT License. Built for the next generation of agentic AI.
