from collections import deque
import time

class SensoryMemory:
    def __init__(self, ttl=60):
        self.memories = {} # user_id -> deque
        self.ttl = ttl

    def add(self, user_id, message):
        if user_id not in self.memories:
            self.memories[user_id] = deque(maxlen=10)
        self.memories[user_id].append({
            "content": message,
            "timestamp": time.time()
        })

    def get(self, user_id):
        if user_id not in self.memories:
            return []
        
        # Filter by TTL
        now = time.time()
        return [m for m in self.memories[user_id] if now - m["timestamp"] < self.ttl]
