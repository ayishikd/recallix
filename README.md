# Recallix
### Universal Memory Substrate for AI Agents

> **0.01ms writes. 0.19ms search. 1M nodes.**
> The first verified cross-model memory transfer 
> between different LLMs.

![Recallix Dashboard](dashboard.png)

## 🚀 Key Performance Audits (Verified)
*   **Instant Write Latency**: 0.01ms (Two-Phase Write Buffer)
*   **Search Latency**: 0.19ms (Avg) at 1,000,000 nodes
*   **Recall Accuracy**: 100/100 (Reproducible stress-test)
*   **Long-Term Retention**: 75% (After 500+ turns of noise)
*   **Multi-Agent Handover**: 100% Fidelity (Model A stores → Model B retrieves)

## The Problem

Every AI agent today is amnesiac. It forgets everything 
between sessions. When you're building multi-agent systems, 
there's no shared memory substrate — each model operates 
in isolation.

Recallix is the persistent cognitive layer that fixes this. 
Any model can write to it. Any model can read from it. 
The memory survives forever.

## 🏛️ Modern Architecture
*   **SIMD Acceleration**: NEON (Apple Silicon, benchmarked). AVX2/SSE (x86, implemented — benchmarks pending).
*   **Two-Phase Cognitive Storage**: Instant write buffer with asynchronous background HNSW construction.
*   **Cognitive Pipeline**: Atomic 12-step store process with **Hybrid Neural-Heuristic Reranking**.
*   **ACID Persistence**: High-velocity ingestion via **SQLite WAL mode**.
*   **Model Agnostic**: Neutral substrate supporting Llama, Mistral, GPT, and custom architectures.

## 📊 Audited Configuration (The Ground Truth)
To replicate our **0.19ms** search and **75% retention** metrics, we used the following defaults:
*   **Reasoning Model**: `llama3.1:8b` (Ollama)
*   **Retrieval Model**: `mistral:latest` (Ollama)
*   **Embedding Model**: `mxbai-embed-large` (Ollama)
*   **HNSW Params**: `M=16`, `efConstruction=100`, `efSearch=50`
*   **Database**: SQLite with `PRAGMA journal_mode=WAL` and `PRAGMA synchronous=NORMAL`
*   **Hardware**: Apple M-series (ARM) with **NEON SIMD** acceleration

> ⚠️ **Hardware Caveat**: Benchmarks were measured on ARM (Apple Silicon). All models and parameters are configurable via `config.yaml`.

---

## 🛠️ Getting Started

### 1. Requirements
*   **Ollama**: Install from [ollama.com](https://ollama.com)
*   **C++17**: For high-performance indexing
*   **Python 3.11+**: For cognitive orchestration

### 2. Pull Required Models (Audited Defaults)
Recallix uses these specific models for our verified benchmarks. Pull them before running:
```bash
ollama pull llama3.1:8b
ollama pull mistral:latest
ollama pull mxbai-embed-large
```
> [!IMPORTANT]
> These are the audited defaults. To use different models (Ollama, OpenAI, Anthropic, etc.) or adjust HNSW parameters, simply update the **`config.yaml`** file in the root directory.

### 3. Quickstart (Reproduction)

#### A. 1M Node HNSW Search (C++)
```bash
cd backend/infra_cpp/build
./benchmark_hnsw
```

#### B. High-Speed Retention Benchmark (Python)
```bash
# Simulates 500 turns in ~8s with hybrid reranking
./venv/bin/python scratch/retention_benchmark.py
```

#### C. Multi-Agent Handover (Python)
```bash
# Model A (Llama) stores secret → Model B (Mistral) retrieves
./venv/bin/python scratch/multi_agent_benchmark.py
```

---

## 📜 License
Apache-2.0
