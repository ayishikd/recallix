import ollama

class ModelRouter:
    def __init__(self):
        self.fast_model = "mistral"
        self.smart_model = "llama3.1:8b"
        self.embedding_model = "bge-small" # placeholder for actual model name in ollama if used

    def route(self, task_type, prompt):
        """
        Routes the task to the appropriate model based on task_type.
        """
        if task_type in ["compression", "summarization", "preprocessing", "cleanup"]:
            return self._query(self.fast_model, prompt)
        elif task_type in ["reasoning", "reflection", "schema_discovery", "predictive_inference", "replay"]:
            return self._query(self.smart_model, prompt)
        else:
            # Default to fast for unknown small tasks, or smart for complex ones
            return self._query(self.fast_model, prompt)

    def _query(self, model, prompt):
        try:
            response = ollama.generate(model=model, prompt=prompt)
            return response['response']
        except Exception as e:
            return f"Error querying local model {model}: {str(e)}"

    def get_embedding(self, text):
        """
        Uses the embedding model.
        """
        try:
            # Assuming 'bge-small' is pulled in ollama
            response = ollama.embeddings(model="mxbai-embed-large", prompt=text) # Using a common one if bge not available
            return response['embedding']
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return []
