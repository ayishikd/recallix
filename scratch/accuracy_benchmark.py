import requests
import json
import time
import random

API_URL = "http://127.0.0.1:8000/memory"
API_KEY = "local_dev_key"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

def store_fact(fact):
    payload = {"content": fact}
    res = requests.post(f"{API_URL}/store", json=payload, headers=HEADERS)
    return res.status_code == 200

def query_fact(query):
    payload = {"query": query}
    res = requests.post(f"{API_URL}/recall", json=payload, headers=HEADERS)
    if res.status_code == 200:
        return res.json()["data"]["memories"]
    return []

def run_benchmark():
    print("🚀 Starting Memory Accuracy Benchmark...")
    
    # 1. Generate 100 Facts
    facts = [
        (f"The hidden password for level {i} is 'alpha-{i*7}'", f"What is the password for level {i}?")
        for i in range(1, 101)
    ]
    
    print(f"📥 Storing 100 facts...")
    for i, (fact, _) in enumerate(facts):
        store_fact(fact)
        if (i+1) % 20 == 0:
            print(f"   Progress: {i+1}/100 facts stored")
            
    # 2. Simulate 50 distraction exchanges
    print(f"🌪️ Injecting 50 distraction messages...")
    distractions = [
        "What's the weather like today?",
        "I'm thinking of buying a new car.",
        "The stock market is quite volatile lately.",
        "Have you seen the latest movie?",
        "I need to go grocery shopping.",
        "How do you bake a chocolate cake?",
        "The sky is very blue today.",
        "I love listening to jazz music in the evening.",
        "What is the capital of France?",
        "Programming in C++ is fun but challenging."
    ]
    for i in range(50):
        store_fact(random.choice(distractions))
        
    # 3. Test Recall
    print(f"🔍 Testing recall on 20 random facts...")
    test_indices = random.sample(range(100), 20)
    correct = 0
    
    for idx in test_indices:
        fact_text, query_text = facts[idx]
        print(f"   Querying: '{query_text}'")
        memories = query_fact(query_text)
        
        # Check if the fact content is in any of the retrieved memories
        found = False
        for m in memories:
            # The memory might be a string or a dict depending on the builder
            content = m if isinstance(m, str) else m.get("content", "")
            if f"alpha-{ (idx+1)*7 }" in content:
                found = True
                break
        
        if found:
            print(f"   ✅ Correct!")
            correct += 1
        else:
            print(f"   ❌ Failed! Top memory was: {memories[0] if memories else 'None'}")
            
    accuracy = (correct / 20) * 100
    print(f"\n📊 BENCHMARK RESULT: {accuracy}% Accuracy ({correct}/20)")
    return accuracy

if __name__ == "__main__":
    run_benchmark()
