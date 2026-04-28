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
        self.provider_cfg = models_cfg.get(self.provider, {})

        self.fast_model = self.provider_cfg.get("fast_model", "mistral:latest")
        self.smart_model = self.provider_cfg.get("smart_model", "llama3.1:8b")
        self.embedding_model = self.provider_cfg.get("embedding_model", "mxbai-embed-large")
        self.base_url = self.provider_cfg.get("base_url", "http://localhost:11434")
        
        # Priority: 1. Environment Variable, 2. config.yaml
        env_key_name = f"{self.provider.upper()}_API_KEY"
        self.api_key = os.getenv(env_key_name) or self.provider_cfg.get("api_key", "")

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
        elif self.provider == "nvidia":
            return self._query_nvidia(model, prompt)
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

    def _query_nvidia(self, model, prompt):
        """Specific implementation for NVIDIA's Nemotron models."""
        try:
            from openai import OpenAI
            
            # Select specific key if available in env, otherwise fallback to default
            current_api_key = self.api_key
            if "nemotron-nano-12b" in model:
                current_api_key = os.getenv("NVIDIA_NEMOTRON_VL_KEY") or current_api_key
            elif "nemotron-nano-9b" in model:
                current_api_key = os.getenv("NVIDIA_NEMOTRON_NANO_KEY") or current_api_key

            client = OpenAI(
                base_url=self.base_url,
                api_key=current_api_key
            )
            
            messages = []
            extra_body = {}
            
            # Nemotron-specific thinking logic
            if "nvidia-nemotron-nano-9b-v2" in model:
                messages.append({"role": "system", "content": "/think"})
                extra_body = {
                    "min_thinking_tokens": 1024,
                    "max_thinking_tokens": 2048
                }
            
            messages.append({"role": "user", "content": prompt})

            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.6,
                top_p=0.95,
                max_tokens=4096,
                extra_body=extra_body if extra_body else None
            )
            
            message = completion.choices[0].message
            full_response = ""
            
            # Handle reasoning_content for Nemotron thinking models
            reasoning = getattr(message, "reasoning_content", None)
            if reasoning:
                full_response += f"<thought>\n{reasoning}\n</thought>\n\n"
            
            full_response += message.content or ""
            return full_response
        except Exception as e:
            print(f"[NVIDIA Error] Model: {model} | Type: {type(e)} | Details: {str(e)}")
            return f"Error querying NVIDIA model {model}: {str(e)}"

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
