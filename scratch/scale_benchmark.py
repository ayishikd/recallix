import requests
import time
import numpy as np
import matplotlib.pyplot as plt
import os
import random

INFRA_URL = "http://localhost:8080"
VECTOR_DIM = 128
NUM_QUERIES = 1000 # Massively increased for statistical stability
WARMUP_RUNS = 100 # To remove cold-start effects

def cpp_search(query, top_k=5):
    start = time.time()
    payload = {"query": query.tolist(), "top_k": top_k}
    headers = {"X-Internal-Key": "Recallix-Core-8892"}
    res = requests.post(f"{INFRA_URL}/search_vector", json=payload, headers=headers)
    end = time.time()
    if res.status_code != 200:
        return None, 0
    data = res.json()
    ids = [r["id"] for r in data["results"]]
    return ids, (end - start) * 1000

def python_numpy_baseline(q, m, ids, k=5):
    s = time.time()
    q_norm = np.linalg.norm(q)
    m_norms = np.linalg.norm(m, axis=1)
    dots = np.dot(m, q)
    scores = dots / (q_norm * m_norms)
    idx = np.argsort(scores)[::-1][:k]
    res_ids = [ids[i] for i in idx]
    return res_ids, (time.time() - s) * 1000

def run_scale_benchmark():
    scales = [1000, 10000, 100000, 1000000]
    cpp_avg_latencies = []
    python_avg_latencies = []
    cpp_all_percentiles = []
    recall_scores = []

    print("🚀 Starting RESEARCH-GRADE Scale Benchmark...")
    print(f"   Rigorous Setup: {NUM_QUERIES} queries per scale | {WARMUP_RUNS} warmup runs")

    for scale in scales:
        print(f"\n📊 Testing Scale: {scale:,} nodes")
        
        # Clear C++
        headers = {"X-Internal-Key": "Recallix-Core-8892"}
        requests.post(f"{INFRA_URL}/clear", headers=headers)

        # 1. Generate Clustered Data (Realistic Semantics)
        num_clusters = 5
        cluster_centers = np.random.randn(num_clusters, VECTOR_DIM)
        raw_vectors = []
        for _ in range(scale):
            center = cluster_centers[np.random.randint(0, num_clusters)]
            noise = np.random.randn(VECTOR_DIM) * 0.1
            raw_vectors.append(center + noise)
        raw_vectors = np.array(raw_vectors).astype('float32')
        raw_vectors /= np.linalg.norm(raw_vectors, axis=1)[:, np.newaxis]
        python_ids = [f"vec_{j}" for j in range(scale)]
        
        # 2. Upload to C++ (Bulk)
        print(f"   📥 Ingesting {scale:,} clustered vectors...")
        chunk_size = 5000
        for i in range(0, scale, chunk_size):
            chunk = []
            for j in range(i, min(i + chunk_size, scale)):
                chunk.append({"id": python_ids[j], "vector": raw_vectors[j].tolist()})
            requests.post(f"{INFRA_URL}/bulk_add", json={"vectors": chunk}, headers=headers)
        
        # 2.5 Wait for Indexing to Complete
        print(f"   ⏳ Waiting for HNSW indexing to complete...")
        start_wait = time.time()
        last_pending = -1
        while True:
            try:
                res = requests.get(f"{INFRA_URL}/status", timeout=2, headers=headers)
                if res.status_code == 200:
                    pending = res.json().get("pending_count", 0)
                    if pending == 0:
                        break
                    if pending != last_pending:
                        print(f"      Indexing... {pending} vectors remaining", end="\r")
                        last_pending = pending
                
                if time.time() - start_wait > 300: # 5 min timeout per scale
                    print(f"\n   ⚠️ Indexing timeout reached! Proceeding anyway...")
                    break
                    
            except Exception as e:
                print(f"\n   ❌ Error checking status: {e}")
                time.sleep(1)
            time.sleep(0.5)
        print(f"   ✅ Indexing phase finished.                        ")
        
        # 3. Generate 1000 Randomized Queries from the dataset
        query_indices = random.sample(range(scale), NUM_QUERIES)
        queries = [raw_vectors[idx] for idx in query_indices]
        
        # 4. Warmup Phase
        print(f"   🔥 Warming up ({WARMUP_RUNS} runs)...")
        for _ in range(WARMUP_RUNS):
            cpp_search(queries[0])
            
        # 5. Benchmark C++ (Latency + Percentiles)
        print(f"   🔍 Benchmarking Recallix (1000 queries)...")
        cpp_runs = []
        for q in queries:
            _, lat = cpp_search(q)
            cpp_runs.append(lat)
        
        cpp_avg_latencies.append(np.mean(cpp_runs))
        cpp_all_percentiles.append({
            "p50": np.percentile(cpp_runs, 50),
            "p95": np.percentile(cpp_runs, 95),
            "p99": np.percentile(cpp_runs, 99)
        })
        
        # 6. Benchmark Python + Recall Validation
        print(f"   🧪 Benchmarking Python & Validating Recall@5...")
        py_runs = []
        overlaps = 0
        
        # Only do all 1000 for Python if scale is small; otherwise sample for time
        py_sample_count = 1000 if scale <= 100000 else 10 # Python is slow at 1M
        
        for i in range(py_sample_count):
            q = queries[i]
            # Exact Ground Truth (Brute Force)
            brute_ids, py_lat = python_numpy_baseline(q, raw_vectors, python_ids)
            py_runs.append(py_lat)
            
            # Get ANN results for the SAME query
            ann_ids, _ = cpp_search(q)
            
            # Calculate Recall@5
            if ann_ids:
                overlap = len(set(brute_ids) & set(ann_ids))
                overlaps += overlap / 5.0
        
        python_avg_latencies.append(np.mean(py_runs))
        recall_scores.append(overlaps / py_sample_count)
        
        print(f"   ✅ Scale {scale:,} | Avg Latency: {np.mean(cpp_runs):.2f}ms | Recall@5: {(overlaps/py_sample_count)*100:.1f}%")

    # 7. Final Rigorous Report
    print(f"\n" + "="*50)
    print(f"📊 FINAL RESEARCH AUDIT REPORT")
    print(f"="*50)
    for i, s in enumerate(scales):
        p = cpp_all_percentiles[i]
        print(f"Scale: {s:9,d} | Avg: {cpp_avg_latencies[i]:.2f}ms | P99: {p['p99']:.2f}ms | Recall@5: {recall_scores[i]*100:5.1f}%")
    print("="*50)

    # 8. Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(scales, python_avg_latencies, label="Python (Linear O(N))", color="#ffffff30", linestyle="--")
    plt.plot(scales, cpp_avg_latencies, label="Recallix (HNSW+NEON)", color="#2563EB", linewidth=3)
    
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Number of Memory Nodes (Log Scale)')
    plt.ylabel('Latency (ms, Log Scale)')
    plt.title('Memory Retrieval Performance: Python vs C++ Core (Research Rigor)')
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.annotate('Python scales linearly (O(N))', xy=(100000, python_avg_latencies[2]), xytext=(10000, 10000),
                 arrowprops=dict(facecolor='white', shrink=0.05, alpha=0.5))
    
    plot_path = "backend/docs/scale_benchmark_rigorous.png"
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)
    plt.savefig(plot_path)
    print(f"\n📈 Rigorous benchmark plot saved to {plot_path}")

def worker_query(q):
    # We must re-init or use the global mm inside the worker process safely
    import os
    import time
    from backend.api.deps import get_memory_manager
    local_mm = get_memory_manager()
    start = time.time()
    local_mm.retrieve("test_user_concurrent", q, limit=5)
    return (time.time() - start) * 1000

def run_concurrency_benchmark():
    from concurrent.futures import ProcessPoolExecutor
    from backend.api.deps import get_memory_manager
    import time
    
    print("\n" + "="*50)
    print("🚀 Starting Concurrency & Throughput Benchmark (Direct Calls)")
    print("="*50)
    
    mm = get_memory_manager()
    user_id = "test_user_concurrent"
    
    # 1. Clear existing
    headers = {"X-Internal-Key": "Recallix-Core-8892"}
    mm.episodic.cleanup_low_importance_memories(user_id) # pseudo clear
    requests.post(f"http://localhost:8080/clear", headers=headers)
    
    # 2. Store test set
    num_docs = 100
    print(f"   📥 Ingesting {num_docs} documents via MemoryManager...")
    for i in range(num_docs):
        mm.store(user_id, f"Project Zephyr status update {i}: all systems green.", skip_llm=True, sync_index=False)
    
    # Wait for indexing
    print("   ⏳ Waiting for index sync...")
    for _ in range(10):
        try:
            res = requests.get("http://localhost:8080/status", timeout=1, headers=headers)
            if res.status_code == 200 and res.json().get("pending_count", 0) == 0:
                break
        except: pass
        time.sleep(0.5)

    # 3. Concurrent Retrieval
    queries = [f"What is the status of Project Zephyr {i}?" for i in range(200)]
    
    print("   🌪️ Firing 200 concurrent queries via ProcessPoolExecutor...")
    start_time = time.time()
    latencies = []
    
    with ProcessPoolExecutor(max_workers=8) as ex:
        results = ex.map(worker_query, queries)
        for lat in results:
            latencies.append(lat)
            
    total_time = time.time() - start_time
    qps = len(queries) / total_time
    
    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)
    
    print(f"   ✅ Concurrency Benchmark Complete")
    print(f"      Total Time: {total_time:.2f}s")
    print(f"      Throughput: {qps:.1f} QPS")
    print(f"      P50 Latency: {p50:.2f} ms")
    print(f"      P95 Latency: {p95:.2f} ms")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_scale_benchmark()
    run_concurrency_benchmark()
