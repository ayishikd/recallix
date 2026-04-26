"""
ModelRouter: Universal LLM provider abstraction.
Loads config from config.yaml and routes to Ollama, OpenAI, Anthropic, Groq,
or any OpenAI-compatible API endpoint.
"""
import os
import yaml
import requests

# Locate config.yaml relative to project root
_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "config.yaml")


def _load_config():
    """Load config.yaml or return sensible defaults."""
    try:
        with open(os.path.abspath(_CONFIG_PATH), "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("[ModelRouter] ⚠️  config.yaml not found — using hardcoded Ollama defaults.")
        return {
            "models": {
                "provider": "ollama",
                "ollama": {
                    "base_url": "http://localhost:11434",
                    "fast_model": "mistral:latest",
                    "smart_model": "llama3.1:8b",
                    "embedding_model": "mxbai-embed-large",
                },
            }
        }


class ModelRouter:
    def __init__(self):
        cfg = _load_config()
        models_cfg = cfg.get("models", {})
        self.provider = models_cfg.get("provider", "ollama")
        self.provider_cfg = models_cfg.get(self.provider, {})

        self.fast_model = self.provider_cfg.get("fast_model", "mistral:latest")
        self.smart_model = self.provider_cfg.get("smart_model", "llama3.1:8b")
        self.embedding_model = self.provider_cfg.get("embedding_model", "mxbai-embed-large")
        self.base_url = self.provider_cfg.get("base_url", "http://localhost:11434")
        self.api_key = self.provider_cfg.get("api_key", "")

        print(f"[ModelRouter] Provider: {self.provider}")
        print(f"[ModelRouter] Fast: {self.fast_model} | Smart: {self.smart_model} | Embedding: {self.embedding_model}")

    def route(self, task_type, prompt):
        """
        Routes the task to the appropriate model based on task_type.
        """
        if task_type in ["compression", "summarization", "preprocessing", "cleanup"]:
            return self._query(self.fast_model, prompt)
        elif task_type in ["reasoning", "reflection", "schema_discovery", "predictive_inference", "replay"]:
            return self._query(self.smart_model, prompt)
        else:
            return self._query(self.fast_model, prompt)

    def _query(self, model, prompt):
        """Dispatch to the correct provider backend."""
        if self.provider == "ollama":
            return self._query_ollama(model, prompt)
        else:
            # OpenAI-compatible API (works for OpenAI, Anthropic, Groq, custom)
            return self._query_openai_compat(model, prompt)

    def _query_ollama(self, model, prompt):
        """Query Ollama's local REST API."""
        try:
            import ollama
            response = ollama.generate(model=model, prompt=prompt)
            return response['response']
        except Exception as e:
            return f"Error querying Ollama model {model}: {str(e)}"

    def _query_openai_compat(self, model, prompt):
        """Query any OpenAI-compatible chat completions API."""
        try:
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
            }
            res = requests.post(url, json=payload, headers=headers, timeout=30)
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error querying {self.provider} model {model}: {str(e)}"

    def get_embedding(self, text):
        """Generate embeddings using the configured provider."""
        if self.provider == "ollama":
            return self._get_embedding_ollama(text)
        else:
            return self._get_embedding_openai_compat(text)

    def _get_embedding_ollama(self, text):
        """Get embeddings from Ollama."""
        try:
            import ollama
            response = ollama.embeddings(model=self.embedding_model, prompt=text)
            return response['embedding']
        except Exception as e:
            print(f"Error getting Ollama embedding: {e}")
            return []

    def _get_embedding_openai_compat(self, text):
        """Get embeddings from any OpenAI-compatible API."""
        try:
            url = f"{self.base_url}/embeddings"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.embedding_model,
                "input": text,
            }
            res = requests.post(url, json=payload, headers=headers, timeout=30)
            res.raise_for_status()
            return res.json()["data"][0]["embedding"]
        except Exception as e:
            print(f"Error getting {self.provider} embedding: {e}")
            return []
