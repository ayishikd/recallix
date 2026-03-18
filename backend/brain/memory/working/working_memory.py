import json
import os

class WorkingMemory:
    def __init__(self, storage_path="backend/storage/working_memory.json"):
        self.storage_path = storage_path
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        return {}

    def _save(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.data, f)

    def update(self, user_id, context_delta):
        if user_id not in self.data:
            self.data[user_id] = {"summary": "", "goals": []}
        
        # Simple update logic: append to summary or update state
        self.data[user_id]["summary"] += f" | {context_delta}"
        self._save()

    def get(self, user_id):
        return self.data.get(user_id, {"summary": "", "goals": []})
