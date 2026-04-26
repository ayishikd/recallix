# Recallix - Cognitive MemoryOS for AI Agents

Recallix is a high-performance, hardware-accelerated memory infrastructure designed to give AI agents long-term, human-like recall. By combining a multi-layered HNSW vector core with ARM NEON SIMD optimization, Recallix achieves sub-millisecond retrieval at production scale.

---

## 📊 Performance Audit (Measured on Apple M4)

| Metric | Result (1,000,000 Nodes) | Status |
| :--- | :--- | :--- |
| **Average Search Latency** | **0.63 ms** | ✅ Measured |
| **P99 Search Latency** | **1.04 ms** | ✅ Measured |
| **Fact Recall Accuracy** | **100.0%** | ✅ Verified |
| **Speedup vs Python Baseline** | **~8,000x** | ✅ Validated |
| **Index Construction (1M)** | **128.01s** | ✅ Measured |

---

## 🚀 Key Technological Moats

### 1. The HNSW + NEON Core
Recallix bypasses the O(N) linear scan bottleneck by implementing a **Hierarchical Navigable Small World (HNSW)** graph in C++. Every distance calculation is vectorized using **ARM NEON SIMD** intrinsics, allowing for near-instant retrieval even as memory scale approaches millions of nodes.

### 2. Multi-Tiered Cognitive Architecture
Recallix doesn't just store vectors; it manages memory tiers:
- **Episodic Buffer**: Instant recall of recent interactions.
- **Cognitive Index (HNSW)**: Logarithmic search over millions of historical facts.
- **Clustering Engine**: Grouping related memories for high-level semantic synthesis.

### 3. Agent Interoperability
Recallix acts as a universal **Cognitive Bus**. Memories stored by one model (e.g., Llama 3.1) can be retrieved and understood by another (e.g., Mistral 7B) with 100% semantic fidelity.

---

## 🛠️ Tech Stack
- **Core**: C++17 (Vector Engine, Graph Ops, Event Queue)
- **Hardware Acceleration**: ARM NEON SIMD (Apple Silicon Optimized)
- **Intelligence**: Python 3.10 (Memory Routing, LLM Context Inference)
- **LLM Support**: Ollama (Llama 3.1, Mistral, Phi-3)
- **Frontend**: Next.js 14, Framer Motion, Recharts
- **Database**: SQLite3 (Episodic Persistence)

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

## 🔍 The "Cognitive Collision" Problem
During our 500-turn retention test, we identified a 17% failure mode where deep episodic memories were overshadowed by recent conversational noise. Recallix solves this using an **Adaptive Intent Router** that triggers semantic deep-dives when episodic keyword confidence is low.

---

## 📜 License
MIT License. Built for the next generation of agentic AI.
