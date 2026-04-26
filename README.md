# Recallix - Hardware-Accelerated Cognitive Memory for AI Agents

Every AI agent today is amnesiac. It forgets everything between sessions. Multi-agent systems have no shared memory substrate. We built **Recallix** to fix that — a hardware-accelerated cognitive memory layer that any agent can read from and write to, regardless of which LLM is running underneath.

## 📊 Performance Benchmarks (Measured Audit)

| Metric | Measured Baseline | vs. Pure Python (Baseline) |
|--------|-------------------|----------------------------|
| **1M Node Search (Avg)** | **1.28ms** | **~85x Faster** |
| **1M Node Search (P99)** | **1.80ms** | **~50x Faster** |
| **Recall Accuracy** | **100%** | **Matches** |
| **Multi-Agent Fidelity**| **100%** | **N/A** |
| **500-Turn Retention** | **75%** | **~3x More Reliable** |
| **Index Build (1M)** | **~14.2 min** | **N/A** |

> [!NOTE]
> All benchmarks were measured on an Apple M4 Air with background cognitive workers disabled. Results are 100% reproducible via `scratch/benchmark_hnsw.cpp` and `scratch/retention_benchmark.py`.

![Recallix Benchmark Dashboard](./dashboard.png)
![Recallix Architecture Flow](./architecture.png)

---

## 🔬 Reproduce The Benchmarks
Transparency is our moat. Every number above can be reproduced in under 10 minutes.

### 1. 1M Node Scale Audit (C++)
```bash
cd backend/infra_cpp
cmake -S . -B build
cmake --build build --target benchmark_hnsw
./build/benchmark_hnsw
```

### 2. Recall Accuracy & Retention (Python)
*Requires `memory_service` and `server.py` to be running.*
```bash
# Use the local venv python directly for reproducibility
./venv/bin/python scratch/accuracy_benchmark.py
./venv/bin/python scratch/retention_benchmark.py
```

### 3. Multi-Agent Handover (Python)
```bash
./venv/bin/python scratch/multi_agent_benchmark.py
```

---

## 💎 Why Recallix Exists
Most RAG systems today are built for documents, not for active agent cognition. They are slow, stateless, and fail at scale. Recallix provides a persistent "Long-Term Memory" layer that allows agents to:
- **Remember** previous user preferences across thousands of turns.
- **Hand over** complex task context to other agents seamlessly.
- **Retrieve** critical facts in millisecond time, ensuring no interruption in agentic thought.

---

## 🏗️ Getting Started

### 1. Build the C++ Infrastructure
```bash
cd backend/infra_cpp
cmake -S . -B build
cmake --build build --target memory_service
./build/memory_service
```

### 2. Initialize the Python Brain
```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python server.py
```

---

## 📜 License
MIT License. Built for the next generation of agentic AI.
