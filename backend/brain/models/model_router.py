"""
ModelRouter: Universal LLM provider abstraction.
Loads config from config.yaml and routes to Ollama, OpenAI, Anthropic, Groq,
or any OpenAI-compatible API endpoint.
"""
import os
import yaml
import requests
from dotenv import load_dotenv

load_dotenv()

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
        
        # Support separate embedding provider (Fix for local embedding request)
        self.embedding_provider = models_cfg.get("embedding_provider", self.provider)
        
        # Primary Config
        self.provider_cfg = models_cfg.get(self.provider, {})
        self.fast_model = self.provider_cfg.get("fast_model", "mistral:latest")
        self.smart_model = self.provider_cfg.get("smart_model", "llama3.1:8b")
        self.base_url = self.provider_cfg.get("base_url", "http://localhost:11434")
        
        # Embedding Config
        self.embed_cfg = models_cfg.get(self.embedding_provider, {})
        self.embedding_model = self.embed_cfg.get("embedding_model", "mxbai-embed-large")
        self.embed_base_url = self.embed_cfg.get("base_url", "http://localhost:11434")
        
        # Auth Keys
        env_key_name = f"{self.provider.upper()}_API_KEY"
        self.api_key = os.getenv(env_key_name) or self.provider_cfg.get("api_key", "")
        
        embed_env_key = f"{self.embedding_provider.upper()}_API_KEY"
        self.embed_api_key = os.getenv(embed_env_key) or self.embed_cfg.get("api_key", "")

        print(f"[ModelRouter] Primary Provider: {self.provider}")
        print(f"[ModelRouter] Embedding Provider: {self.embedding_provider}")
        print(f"[ModelRouter] Fast: {self.fast_model} | Smart: {self.smart_model} | Embedding: {self.embedding_model}")

    def route(self, task_type, prompt):
        if task_type in ["compression", "summarization", "preprocessing", "cleanup"]:
            return self._query(self.fast_model, prompt)
        elif task_type in ["reasoning", "reflection", "schema_discovery", "predictive_inference", "replay"]:
            return self._query(self.smart_model, prompt)
        else:
            return self._query(self.fast_model, prompt)

    def _query(self, model, prompt):
        if self.provider == "ollama":
            return self._query_ollama(model, prompt)
        elif self.provider == "nvidia":
            return self._query_nvidia(model, prompt)
        else:
            return self._query_openai_compat(model, prompt)

    def _query_ollama(self, model, prompt):
        try:
            import ollama
            response = ollama.generate(model=model, prompt=prompt)
            return response['response']
        except Exception as e:
            return f"Error querying Ollama: {str(e)}"

    def _query_openai_compat(self, model, prompt):
        try:
            url = f"{self.base_url}/chat/completions"
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}
            res = requests.post(url, json=payload, headers=headers, timeout=30)
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error querying {self.provider}: {str(e)}"

    def _query_nvidia(self, model, prompt):
        try:
            from openai import OpenAI
            current_api_key = self.api_key
            client = OpenAI(base_url=self.base_url, api_key=current_api_key)
            messages = []
            extra_body = {}
            if "nvidia-nemotron-nano-9b-v2" in model:
                messages.append({"role": "system", "content": "/think"})
                extra_body = {"min_thinking_tokens": 1024, "max_thinking_tokens": 2048}
            messages.append({"role": "user", "content": prompt})
            completion = client.chat.completions.create(
                model=model, messages=messages, temperature=0.6, top_p=0.95, max_tokens=4096,
                extra_body=extra_body if extra_body else None
            )
            message = completion.choices[0].message
            full_response = ""
            reasoning = getattr(message, "reasoning_content", None)
            if reasoning: full_response += f"<thought>\n{reasoning}\n</thought>\n\n"
            full_response += message.content or ""
            return full_response
        except Exception as e:
            return f"Error querying NVIDIA: {str(e)}"

    def get_embedding(self, text):
        """Generate embeddings using the configured embedding provider."""
        if self.embedding_provider == "ollama":
            return self._get_embedding_ollama(text)
        else:
            return self._get_embedding_openai_compat(text)

    def _get_embedding_ollama(self, text):
        try:
            import ollama
            # Use specific embedding base_url if different from main
            client = ollama.Client(host=self.embed_base_url)
            response = client.embeddings(model=self.embedding_model, prompt=text)
            return response['embedding']
        except Exception as e:
            print(f"Error getting Ollama embedding: {e}")
            return []

    def _get_embedding_openai_compat(self, text):
        try:
            url = f"{self.embed_base_url}/embeddings"
            headers = {"Authorization": f"Bearer {self.embed_api_key}", "Content-Type": "application/json"}
            payload = {"model": self.embedding_model, "input": text}
            res = requests.post(url, json=payload, headers=headers, timeout=30)
            res.raise_for_status()
            return res.json()["data"][0]["embedding"]
        except Exception as e:
            print(f"Error getting {self.embedding_provider} embedding: {e}")
            return []
