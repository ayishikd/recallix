import os
import json
import time
from ..models.model_router import ModelRouter

class CompressionWorker:
    def __init__(self, storage_path="backend/storage/conversation_summaries/"):
        self.storage_path = storage_path
        self.router = ModelRouter()
        os.makedirs(self.storage_path, exist_ok=True)

    def compress_conversations(self, user_id, messages):
        """
        Level 1: Conversation Compression
        Input: 50-100 raw messages (simplified here)
        Output: short conversation summary
        """
        if not messages:
            return
            
        prompt = f"Summarize the following user conversation concisely:\n\n" + "\n".join(messages)
        summary = self.router.route("compression", prompt)
        
        filename = f"{user_id}_{int(time.time())}.json"
        filepath = os.path.join(self.storage_path, filename)
        
        with open(filepath, 'w') as f:
            json.dump({
                "user_id": user_id,
                "summary": summary,
                "timestamp": time.time(),
                "message_count": len(messages)
            }, f)
        
        return summary

    def compress_topics(self, user_id):
        """
        Level 2: Topic Compression (Placeholder)
        Input: 10-20 conversation summaries
        """
        # Logic to read files in storage_path and combine them
        pass
