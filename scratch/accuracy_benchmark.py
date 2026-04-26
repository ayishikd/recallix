import requests
import time
import random

API_URL = "http://127.0.0.1:8000/memory"
API_KEY = "local_dev_key"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
TEST_USER = "test_user_acc"

FACTS = [
    f"Fact {i}: The atomic weight of element {i} is approximately {round(i*1.1, 2)}" for i in range(1, 101)
]

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

    print(f"🔍 Testing Recall Accuracy (20 random facts)...")
    correct = 0
    test_indices = random.sample(range(100), 20)
    
    for idx in test_indices:
        query = f"What is the atomic weight of element {idx+1}?"
        res = requests.post(f"{API_URL}/recall", json={"query": query, "user_id": TEST_USER}, headers=HEADERS)
        if res.status_code == 200:
            mems = res.json()["data"]["memories"]
            if mems and str(round((idx+1)*1.1, 2)) in mems[0]["content"]:
                correct += 1
                print(f"   ✅ Correct: Fact {idx+1}")
            else:
                print(f"   ❌ Miss: Fact {idx+1}")
    
    accuracy = (correct / 20) * 100
    print(f"\n📊 FINAL ACCURACY: {accuracy}%")

if __name__ == "__main__":
    run_accuracy_benchmark()
