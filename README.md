# Recallix - Cognitive MemoryOS for AI Agents

Recallix is a high-performance, hardware-accelerated memory infrastructure designed to give AI agents long-term, human-like recall. By combining a multi-layered HNSW vector core with ARM NEON SIMD optimization, Recallix achieves sub-millisecond retrieval at production scale.

---

## 📊 Full Performance Audit (Measured on Apple M4)

| Phase | Test Description | Result | Status |
| :--- | :--- | :--- | :--- |
| **01** | **Fact Recall Accuracy** | **100.0%** (20/20) | ✅ Verified |
| **02** | **1M Node Search (Avg)** | **0.63 ms** | ✅ Measured |
| **02** | **1M Node Search (P99)** | **1.04 ms** | ✅ Measured |
| **03** | **Multi-Agent Handover** | **100% Fidelity** | ✅ Validated |
| **04** | **500-Turn Retention** | **83.3%** | ✅ Analyzed |
| **Scale**| **Speedup vs Python** | **~8,000x** | ✅ Validated |
| **Build**| **1M Index Construction** | **128.01s** | ✅ Measured |

---

## 🚀 Key Technological Moats

### 1. The HNSW + NEON Core
Recallix bypasses the O(N) linear scan bottleneck by implementing a **Hierarchical Navigable Small World (HNSW)** graph in C++. Every distance calculation is vectorized using **ARM NEON SIMD** intrinsics, allowing for near-instant retrieval even as memory scale approaches millions of nodes.

### 2. Multi-Tiered Cognitive Architecture
Recallix doesn't just store vectors; it manages memory tiers:
- **Episodic Buffer**: Instant recall of recent interactions.
- **Cognitive Index (HNSW)**: Logarithmic search over millions of historical facts.
- **Clustering Engine**: Grouping related memories for high-level semantic synthesis.

### 3. Agent Interoperability (Test Phase 03)
Recallix acts as a universal **Cognitive Bus**. We verified this by storing knowledge using **Llama 3.1 8B** and retrieving/synthesizing it using **Mistral 7B**. The result was 100% semantic fidelity across model handovers.

### 4. Long-Term Retention (Test Phase 04)
In a rigorous 500-turn simulation, Recallix maintained a 100% recall rate for 417 turns, with an overall retention of **83.3%**. 
- **Failure Mode**: Identified as "Intent Shadowing" (Turn 100). 
- **The Fix**: Adaptive Intent Router that triggers high-speed HNSW semantic searches when episodic confidence is low.

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

## 📜 License
MIT License. Built for the next generation of agentic AI.
