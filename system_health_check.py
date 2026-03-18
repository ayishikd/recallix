import requests
import json
import time

BASE_URL = "http://localhost:8000"
API_KEY = "local_dev_key"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

def run_test_single_agent():
    print("\n[TEST] Single Agent Verification")
    content = f"Single agent test memory at {time.time()}"
    store_resp = requests.post(f"{BASE_URL}/memory/store", json={"content": content}, headers=HEADERS)
    if store_resp.status_code == 200:
        print("✅ Store Success")
        recall_resp = requests.post(f"{BASE_URL}/memory/recall", json={"query": "Single agent test"}, headers=HEADERS)
        if recall_resp.status_code == 200:
            print("✅ Recall Success")
            return True
    print("❌ Single Agent Test Failed")
    return False

def run_test_multi_agent():
    print("\n[TEST] Multi-Agent Verification")
    # 1. List agents
    list_resp = requests.get(f"{BASE_URL}/agents/list", headers=HEADERS)
    if list_resp.status_code != 200:
        print("❌ Failed to list agents")
        return False
    print(f"✅ Agents Registered: {len(list_resp.json()['data'])}")

    # 2. Store isolated memories
    agent_a = "ResearchAgent"
    agent_b = "PlannerAgent"
    
    requests.post(f"{BASE_URL}/agents/store", json={"content": "Private research for A", "agent_id": agent_a, "memory_type": "private"}, headers=HEADERS)
    requests.post(f"{BASE_URL}/agents/store", json={"content": "Private plan for B", "agent_id": agent_b, "memory_type": "private"}, headers=HEADERS)
    
    # 3. Verify isolation
    recall_a = requests.post(f"{BASE_URL}/agents/recall", json={"query": "research", "agent_id": agent_a}, headers=HEADERS).json()
    recall_b = requests.post(f"{BASE_URL}/agents/recall", json={"query": "research", "agent_id": agent_b}, headers=HEADERS).json()
    
    found_a = any("Private research" in m["content"] for m in recall_a["data"]["final_memories"])
    found_b_isolation = not any("Private research" in m["content"] for m in recall_b["data"]["final_memories"])
    
    if found_a and found_b_isolation:
        print("✅ Isolation Verified (A sees its own, B doesn't see A's)")
        return True
    else:
        print(f"❌ Isolation Failed. Found A: {found_a}, B Isolated: {found_b_isolation}")
        return False

def run_test_ame():
    print("\n[TEST] AME Verification")
    schema_resp = requests.get(f"{BASE_URL}/agents/schemas", headers=HEADERS)
    if schema_resp.status_code == 200:
        schemas = schema_resp.json()["data"]
        print(f"✅ Evolved Schemas found: {len(schemas)}")
        for s in schemas:
            print(f"  - {s['name']} (v{s['schema_id']})")
        return True
    print("❌ AME Registry Check Failed")
    return False

def run_test_intent():
    print("\n[TEST] Intent Classifier Verification")
    tests = [
        ("How do I learn Python?", "learning"),
        ("I love the color blue.", "preference_update"),
        ("Compare React and Vue.", "research"),
        ("Start the build process.", "task_execution"),
        ("Hello world.", "conversation")
    ]
    
    passed = 0
    for query, expected in tests:
        resp = requests.post(f"{BASE_URL}/memory/recall", json={"query": query}, headers=HEADERS).json()
        detected = resp["data"]["intent"]
        if detected == expected:
            passed += 1
            print(f"✅ Query: '{query}' -> {detected}")
        else:
            print(f"❌ Query: '{query}' -> {detected} (Expected: {expected})")
            
    print(f"✅ Intent Accuracy: {passed}/{len(tests)}")
    return passed == len(tests)

if __name__ == "__main__":
    print("🚀 Starting MemoryOS Full System Health Check")
    results = [
        run_test_single_agent(),
        run_test_multi_agent(),
        run_test_ame(),
        run_test_intent()
    ]
    
    if all(results):
        print("\n✨ ALL SYSTEMS GO! MemoryOS is fully operational.")
    else:
        print("\n⚠️ SYSTEM WARNING: Some modules failed health check.")
