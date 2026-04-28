import requests
import time

API_URL = "http://127.0.0.1:8000/memory"
API_KEY = "local_dev_key"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
TEST_USER = "test_user_ret"

def run_retention_benchmark():
    print(f"🧹 Clearing memory namespace for {TEST_USER}...")
    requests.post("http://127.0.0.1:8000/internal/clear", json={"user_id": TEST_USER}, headers=HEADERS)

    print(f"🚀 Starting Long-Term Retention Benchmark...")
    print(f"📥 Simulating 500 turns of conversation (Audit Mode: HIGH SPEED)...")
    
    start_time = time.time()
    important_turns = {
        10:  "The user's favorite color is midnight blue.",
        100: "The project deadline is December 12th.",
        250: "The user has a cat named Pixel.",
        400: "The meeting is at 2 PM tomorrow."
    }
    
    TOPICS = ["the weather in Tokyo", "stock market fluctuations", "a recipe for lasagna", "the history of the Eiffel Tower", "how to build a treehouse", "quantum entanglement", "the rules of cricket", "deep sea exploration"]
    for i in range(500):
        content = important_turns.get(i, f"Turn {i}: Discussion about {TOPICS[i % len(TOPICS)]}.")
        requests.post(f"{API_URL}/store", json={"content": content, "user_id": TEST_USER, "skip_llm": True}, headers=HEADERS)
        if i % 100 == 0:
            print(f"   Processed {i}/500 turns...")
    
    end_time = time.time()
    print(f"✅ 500 turns simulated in {end_time - start_time:.2f} seconds.")

    print(f"🔍 Testing Retention (Querying for deep facts)...")
    
    # Use natural recall queries — the way a real user would ask
    recall_queries = {
        10:  "What is the user's favorite color?",
        100: "When is the project deadline?",
        250: "Does the user have any pets?",
        400: "When is the meeting?"
    }
    
    correct = 0
    for turn, fact in important_turns.items():
        query = recall_queries[turn]
        res = requests.post(f"{API_URL}/recall", json={"query": query, "user_id": TEST_USER}, headers=HEADERS)
        if res.status_code == 200:
            mems = res.json()["data"]["memories"]
            # Check if any memory contains a distinctive keyword from the fact
            keywords = {
                10: "midnight blue",
                100: "december 12",
                250: "pixel",
                400: "2 pm"
            }
            key = keywords[turn].lower()
            if mems and any(key in m.get("content", "").lower() for m in mems):
                correct += 1
                print(f"   ✅ Retained: Fact from turn {turn} (found '{keywords[turn]}')")
            else:
                print(f"   ❌ Lost: Fact from turn {turn} (looking for '{keywords[turn]}')")
                if mems:
                    print(f"      Got: {mems[0].get('content', 'N/A')[:60]}...")
    
    score = (correct / len(important_turns)) * 100
    print(f"\n📊 RETENTION SCORE: {score}%")

if __name__ == "__main__":
    run_retention_benchmark()
