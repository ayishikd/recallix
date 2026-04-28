import requests
import time
import uuid
import random

API_URL = "http://127.0.0.1:8000/memory"
CLEAR_URL = "http://127.0.0.1:8000/internal/clear"

API_KEY = "local_dev_key"
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

TEST_USER = "test_user_ret_hard"

# Unique benchmark namespace to prevent stale-memory contamination
RUN_ID = str(uuid.uuid4())[:8]

TOPICS = [
    "the weather in Tokyo",
    "stock market fluctuations",
    "a recipe for lasagna",
    "the history of the Eiffel Tower",
    "how to build a treehouse",
    "quantum entanglement",
    "the rules of cricket",
    "deep sea exploration"
]


# -------------------------------------------------------------------
# HARD RETENTION TEST
#
# Tests:
# - Long-term retention
# - Entity disambiguation
# - Conflicting memories
# - Temporal updates
# - Symbolic precision
# - Contextual arbitration
# -------------------------------------------------------------------

IMPORTANT_MEMORIES = {
    10: {
        "content": f"[RUN:{RUN_ID}] Project Alpha deadline is December 12.",
        "query": "When is Project Alpha due?",
        "expected": "december 12"
    },
    40: {
        "content": f"[RUN:{RUN_ID}] Project Beta deadline is December 21.",
        "query": "When is Project Beta due?",
        "expected": "december 21"
    },
    80: {
        "content": f"[RUN:{RUN_ID}] The user's cat is named Pixel.",
        "query": "What is the user's cat named?",
        "expected": "pixel"
    },
    120: {
        "content": f"[RUN:{RUN_ID}] The user's dog is named Pixel.",
        "query": "What is the user's dog named?",
        "expected": "pixel"
    },
    180: {
        "content": f"[RUN:{RUN_ID}] Meeting for Project Orion is at 2 PM.",
        "query": "When is the Project Orion meeting?",
        "expected": "2 pm"
    },
    220: {
        "content": f"[RUN:{RUN_ID}] Meeting for Project Phoenix is at 4 PM.",
        "query": "When is the Project Phoenix meeting?",
        "expected": "4 pm"
    },
    # Temporal update / evolving truth
    300: {
        "content": f"[RUN:{RUN_ID}] The Project Alpha deadline was moved to December 18.",
        "query": "What is the latest Project Alpha deadline?",
        "expected": "december 18"
    },
    # Contradictory distractor
    350: {
        "content": f"[RUN:{RUN_ID}] The Project Alpha deadline is NOT December 12 anymore.",
        "query": "What is the latest Project Alpha deadline?",
        "expected": "december 18"
    }
}


def clear_namespace():
    print(f"🧹 Clearing memory namespace for {TEST_USER}...")
    requests.post(
        CLEAR_URL,
        json={"user_id": TEST_USER},
        headers=HEADERS
    )


def store_memory(content):
    return requests.post(
        f"{API_URL}/store",
        json={
            "content": content,
            "user_id": TEST_USER,
            "skip_llm": True
        },
        headers=HEADERS
    )


def recall(query):
    return requests.post(
        f"{API_URL}/recall",
        json={
            "query": query,
            "user_id": TEST_USER
        },
        headers=HEADERS
    )


def run_retention_benchmark():
    clear_namespace()

    print("\n🚀 Starting HARD Long-Term Retention Benchmark...")
    print(f"🧠 Benchmark Run ID: {RUN_ID}")
    print("📥 Simulating 500 conversational turns with collisions and evolving facts...\n")

    start_time = time.time()

    for i in range(500):

        if i in IMPORTANT_MEMORIES:
            content = IMPORTANT_MEMORIES[i]["content"]
        else:
            topic = random.choice(TOPICS)
            content = f"[RUN:{RUN_ID}] Turn {i}: Discussion about {topic}."

        store_memory(content)

        if i % 100 == 0:
            print(f"   Processed {i}/500 turns...")

    end_time = time.time()

    print(f"\n✅ Simulation completed in {end_time - start_time:.2f} seconds.\n")

    print("🔍 Testing Retention Precision Under Competition...\n")

    total = 0
    correct = 0

    for turn, test_case in IMPORTANT_MEMORIES.items():

        query = test_case["query"]
        expected = test_case["expected"]

        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🧪 Query: {query}")

        res = recall(query)

        if res.status_code != 200:
            print("❌ Recall request failed.")
            continue

        mems = res.json()["data"]["memories"]

        if not mems:
            print("❌ No memories returned.")
            total += 1
            continue

        top_memory = mems[0].get("content", "")

        print(f"📋 Top Memory:")
        print(f"   {top_memory}")

        if expected.lower() in top_memory.lower():
            print("✅ Correct retrieval.")
            correct += 1
        else:
            print(f"❌ Incorrect retrieval.")
            print(f"   Expected keyword: {expected}")

        total += 1

    score = (correct / total) * 100 if total else 0

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 HARD RETENTION REPORT")
    print(f"   Recall@1 Precision: {score:.1f}%")
    print(f"   Correct Top Retrievals: {correct}/{total}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")


if __name__ == "__main__":
    run_retention_benchmark()