import requests
import numpy as np
import time
import random

INFRA_URL = "http://localhost:8080"
VECTOR_DIM = 128
headers = {"X-Internal-Key": "Recallix-Core-8892"}

def test_recall(scale, num_clusters, noise):
    requests.post(f"{INFRA_URL}/clear", headers=headers)
    cluster_centers = np.random.randn(num_clusters, VECTOR_DIM)
    raw_vectors = []
    for _ in range(scale):
        center = cluster_centers[np.random.randint(0, num_clusters)]
        raw_vectors.append(center + np.random.randn(VECTOR_DIM) * noise)
    raw_vectors = np.array(raw_vectors).astype('float32')
    raw_vectors /= np.linalg.norm(raw_vectors, axis=1)[:, np.newaxis]
    python_ids = [f"vec_{j}" for j in range(scale)]
    
    chunk = []
    for j in range(scale):
        chunk.append({"id": python_ids[j], "vector": raw_vectors[j].tolist()})
    requests.post(f"{INFRA_URL}/bulk_add", json={"vectors": chunk}, headers=headers)
    
    while True:
        res = requests.get(f"{INFRA_URL}/status", timeout=2, headers=headers)
        if res.json().get("pending_count", 0) == 0:
            break
        time.sleep(0.1)
        
    queries = [raw_vectors[idx] for idx in random.sample(range(scale), 100)]
    
    overlaps = 0
    for q in queries:
        # baseline
        q_norm = np.linalg.norm(q)
        m_norms = np.linalg.norm(raw_vectors, axis=1)
        dots = np.dot(raw_vectors, q)
        scores = dots / (q_norm * m_norms)
        brute_ids = [python_ids[i] for i in np.argsort(scores)[::-1][:5]]
        
        # hnsw
        res = requests.post(f"{INFRA_URL}/search_vector", json={"query": q.tolist(), "top_k": 5}, headers=headers).json()
        ann_ids = [r["id"] for r in res["results"]]
        
        overlaps += len(set(brute_ids) & set(ann_ids)) / 5.0
        
    return overlaps / 100

print("Dense (clusters=5, noise=0.1):", test_recall(10000, 5, 0.1))
print("Uniform-ish (clusters=1000, noise=1.0):", test_recall(10000, 1000, 1.0))
