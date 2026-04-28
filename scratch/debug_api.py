import requests

API_URL = "http://127.0.0.1:8000/memory"
API_KEY = "local_dev_key"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

payload = {
    "user_id": "test_user_multi",
    "agent_id": "agent_b",
    "query": "What is the secret project code?",
    "limit": 5
}
res = requests.post(f"{API_URL}/recall", json=payload, headers=HEADERS)
print(res.json())
