import spacy
import numpy as np

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = None

class ContextInference:
    def __init__(self, memory_manager):
        self.memory = memory_manager

    def infer(self, query, intent_data, agent_id="default_agent"):
        """
        Determines the topic, domain, and user state.
        Identifies relevant memory types based on intent routing rules.
        """
        doc = nlp(query) if nlp else None
        
        # 1. Topic & Entity Detection
        entities = []
        if doc:
            entities = [ent.text for ent in doc.ents if ent.label_ not in ["CARDINAL", "DATE", "TIME"]]
            if not entities:
                entities = [chunk.text for chunk in doc.noun_chunks 
                           if not any(token.pos_ == "PRON" for token in chunk) and len(chunk.text) > 2]

        # 2. Domain Inference
        domain = "general"
        tech_keywords = ["code", "python", "javascript", "algorithm", "recursion", "stack", "api"]
        if any(kw in query.lower() for kw in tech_keywords):
            domain = "computer_science"
        elif doc and any(ent.label_ in ["MONEY", "ORG"] for ent in doc.ents):
            domain = "business"

        # 3. Memory Type Selection (Strictly following Router Rules)
        intent = intent_data["intent"]
        memory_types = []
        
        if intent == "learning":
            memory_types = ["semantic", "knowledge_graph", "learning_history"]
        elif intent == "task_execution":
            memory_types = ["episodic", "insight"]
        elif intent == "research":
            memory_types = ["semantic", "insight"]
        elif intent == "conversation":
            memory_types = ["recent_episodic", "semantic"]
        elif intent == "preference_update":
            memory_types = ["long_term", "preference"]
        elif intent == "memory_store":
            memory_types = ["episodic"]
        else:
            memory_types = ["episodic"]

        return {
            "topic": entities[0] if entities else "general",
            "domain": domain,
            "user_state": intent,
            "memory_types": memory_types,
            "entities": entities
        }
