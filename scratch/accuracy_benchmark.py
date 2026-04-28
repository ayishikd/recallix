import requests
import time
import random

API_URL = "http://127.0.0.1:8000/memory"
API_KEY = "local_dev_key"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
TEST_USER = "test_user_acc"

PROCESSES = ["synchrotron radiation", "inverse Compton scattering", "thermal bremsstrahlung", "blackbody radiation", "pion decay"]
# Each galaxy has a PRIMARY cause (to be queried) and two secondary/distractor observations
FACTS = []
for i in range(1, 101):
    primary = PROCESSES[i % len(PROCESSES)]
    distractors = [p for p in PROCESSES if p != primary]
    random.shuffle(distractors)
    
    FACTS.append(f"Galaxy X-{i} Primary Emission: {primary}.")
    FACTS.append(f"Galaxy X-{i} Secondary Signature: {distractors[0]}.")
    FACTS.append(f"Galaxy X-{i} Tertiary Trace: {distractors[1]}.")

def run_accuracy_benchmark():
    print(f"🧹 Clearing memory namespace for {TEST_USER}...")
    requests.post("http://127.0.0.1:8000/internal/clear", json={"user_id": TEST_USER}, headers=HEADERS)

    print(f"🚀 Starting Memory Accuracy Benchmark...")
    print(f"📥 Storing 100 facts (Audit Mode: HIGH SPEED)...")
    
    start_time = time.time()
    for fact in FACTS:
        requests.post(f"{API_URL}/store", json={"content": fact, "user_id": TEST_USER, "skip_llm": True}, headers=HEADERS)
    
    end_time = time.time()
    print(f"✅ 100 facts stored in {end_time - start_time:.2f} seconds.")

    print(f"🔍 Testing Recall@K & MRR (20 random galaxies)...")
    recall_at_1 = 0
    recall_at_5 = 0
    mrr_sum = 0
    test_indices = random.sample(range(1, 101), 20)
    
    for idx in test_indices:
        query = f"What is the primary cause of photon emission in Galaxy X-{idx}?"
        res = requests.post(f"{API_URL}/recall", json={"query": query, "user_id": TEST_USER, "top_k": 5}, headers=HEADERS)
        if res.status_code == 200:
            mems = res.json()["data"]["memories"]
            expected_process = PROCESSES[idx % len(PROCESSES)]
            
            found_rank = -1
            for rank, m in enumerate(mems):
                if expected_process in m["content"] and "Primary" in m["content"]:
                    found_rank = rank + 1
                    break
            
            if found_rank == 1:
                recall_at_1 += 1
                print(f"   ✅ [R@1] Galaxy X-{idx} -> {expected_process}")
            elif found_rank > 1:
                recall_at_5 += 1
                print(f"   ⚠️ [R@{found_rank}] Galaxy X-{idx} -> {expected_process} (Ranked Low)")
            else:
                print(f"   ❌ [MISS] Galaxy X-{idx}")
            
            if found_rank != -1:
                mrr_sum += 1.0 / found_rank
    
    count = len(test_indices)
    print(f"\n📊 ACCURACY REPORT (Hardened with Distractors):")
    print(f"   Recall@1: {(recall_at_1/count)*100:.1f}%")
    print(f"   Recall@5: {((recall_at_1 + recall_at_5)/count)*100:.1f}%")
    print(f"   MRR:      {mrr_sum/count:.3f}")

if __name__ == "__main__":
    run_accuracy_benchmark()
