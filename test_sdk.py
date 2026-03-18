import sys
import os
import time

# Add SDK to path
sys.path.append(os.path.join(os.getcwd(), "sdk", "python"))

from memoryos import Memory

def test_sdk():
    print("--- Testing Python SDK ---")
    
    # Initialize with local dev key
    mem = Memory(api_key="local_dev_key", base_url="http://localhost:8000")
    
    # 1. Store
    print("Storing memory...")
    res = mem.store("The user is testing the new Developer SDK.")
    print(f"Store Response: {res}")
    
    # 2. Recall
    print("Recalling memory...")
    res = mem.recall("Testing SDK")
    print(f"Recall Result: {res}")
    
    # 3. Timeline
    print("Fetching timeline...")
    res = mem.timeline()
    print(f"Timeline Result: {res['status']}")
    
    # 4. Insights
    print("Fetching insights...")
    res = mem.insights()
    print(f"Insights Result: {res['status']}")

if __name__ == "__main__":
    test_sdk()
