import requests
import json
import time
import ollama

API_URL = "http://127.0.0.1:8000/memory"
API_KEY = "local_dev_key"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

MODEL_A = "llama3.1:8b"
MODEL_B = "mistral:latest"

def get_llm_response(model, prompt):
    response = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
    return response['message']['content']

def store_memory(agent_id, content, m_type="shared"):
    payload = {
        "content": content,
        "agent_id": agent_id,
        "memory_type": m_type
    }
    res = requests.post(f"{API_URL}/store", json=payload, headers=HEADERS)
    return res.status_code == 200

def recall_memory(agent_id, query):
    payload = {
        "query": query,
        "agent_id": agent_id
    }
    res = requests.post(f"{API_URL}/recall", json=payload, headers=HEADERS)
    if res.status_code == 200:
        return res.json()["data"]["memories"]
    return []

def run_multi_agent_benchmark():
    print(f"🚀 Starting Multi-Agent Memory Benchmark...")
    print(f"👥 Agents: {MODEL_A} (Source) -> {MODEL_B} (Target)")
    
    # 1. Agent A generates a secret fact
    print(f"\n1️⃣ Agent A ({MODEL_A}) creating a memory...")
    prompt_a = "Create a unique secret password for a fictional project. Only output the password, nothing else."
    secret_fact = get_llm_response(MODEL_A, prompt_a).strip()
    print(f"   [Llama] Secret generated: '{secret_fact}'")
    
    # 2. Store in MemoryOS
    start_store = time.time()
    store_memory("llama_agent", f"The project secret password is {secret_fact}", m_type="shared")
    end_store = time.time()
    print(f"   💾 Stored in MemoryOS (Shared) | Latency: {(end_store - start_store)*1000:.2f}ms")
    
    # 3. Agent B queries for the fact
    print(f"\n2️⃣ Agent B ({MODEL_B}) retrieving memory...")
    query = "What is the secret password for the project?"
    
    start_recall = time.time()
    memories = recall_memory("mistral_agent", query)
    end_recall = time.time()
    
    print(f"   🔍 Recall Response Latency: {(end_recall - start_recall)*1000:.2f}ms")
    
    # 4. Agent B uses the memory to answer
    print(f"\n3️⃣ Agent B ({MODEL_B}) formulating final answer...")
    if memories:
        context = memories[0]["content"] if isinstance(memories[0], dict) else memories[0]
        prompt_b = f"Based on this memory: '{context}', answer the question: '{query}'. Be concise."
        final_answer = get_llm_response(MODEL_B, prompt_b).strip()
        print(f"   [Mistral] Final Answer: '{final_answer}'")
        
        # 5. Verification
        if secret_fact.lower() in final_answer.lower():
            print(f"\n✅ SUCCESS: Multi-agent memory transfer verified!")
            print(f"   Consistency: High (Exact match found)")
        else:
            print(f"\n❌ FAILURE: Agent B could not correctly use Agent A's memory.")
    else:
        print(f"\n❌ FAILURE: No memories retrieved for Agent B.")

if __name__ == "__main__":
    run_multi_agent_benchmark()
