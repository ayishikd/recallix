import json
import os
from backend.utils.paths import get_db_path, ensure_dir

class WorkingMemory:
    def __init__(self, storage_path=None):
        self.storage_path = storage_path or get_db_path("backend/storage/working_memory.json")
        ensure_dir(self.storage_path)
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
            self.data[user_id] = {"summary": "", "history": []}
        
        # Implement sliding window of last 15 items
        history = self.data[user_id].get("history", [])
        history.append(context_delta)
        if len(history) > 15:
            history = history[-15:]
        
        self.data[user_id]["history"] = history
        self.data[user_id]["summary"] = " | ".join(history)
        self._save()

    def get(self, user_id):
        return self.data.get(user_id, {"summary": "", "goals": []})
