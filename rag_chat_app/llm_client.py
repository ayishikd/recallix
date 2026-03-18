import requests
import json

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url

    def generate(self, model, system_prompt, user_query, memories):
        """
        RAG Enhanced Generation
        """
        # Augment prompt with memories
        memory_context = "\n".join([m.get('content', '') for m in memories]) if memories else "No relevant memories found."
        
        full_prompt = (
            f"System: {system_prompt}\n\n"
            f"Context from memories:\n{memory_context}\n\n"
            f"User: {user_query}\n\n"
            f"Assistant:"
        )

        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": False
        }

        try:
            res = requests.post(f"{self.base_url}/api/generate", json=payload)
            if res.status_code == 200:
                return res.json().get("response", "No response from model.")
            else:
                return f"Error from Ollama: {res.status_code} - {res.text}"
        except Exception as e:
            return f"Failed to connect to Ollama: {str(e)}"

    def chat(self, model, messages):
        """
        Direct chat without RAG augmentation (optional)
        """
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        try:
            res = requests.post(f"{self.base_url}/api/chat", json=payload)
            return res.json().get("message", {}).get("content", "")
        except Exception as e:
            return f"Chat failed: {str(e)}"
