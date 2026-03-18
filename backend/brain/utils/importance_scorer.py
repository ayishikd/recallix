import numpy as np
import time

class ImportanceScorer:
    @staticmethod
    def calculate(content, context_summary, metadata=None):
        """
        Calculates importance based on novelty, relevance, frequency, and task priority.
        Returns a score between 1 and 10.
        """
        # Mocking novelty score (1-3)
        # In a real system, this would compare embeddings to existing memories
        novelty = 2.0 
        
        # Mocking relevance score (1-3) based on presence of keywords in context
        relevance = 1.0
        if context_summary and any(word in context_summary.lower() for word in content.lower().split()):
            relevance = 3.0
            
        # Mocking frequency/repetition (1-2)
        # If the user repeats something, it's likely more important
        frequency = 1.0
        
        # Mocking task priority (1-2)
        # Logic to detect goals or tasks
        priority = 1.0
        goal_keywords = ["goal", "task", "need to", "must", "important", "remember"]
        if any(kw in content.lower() for kw in goal_keywords):
            priority = 2.0
            
        # final_importance = novelty * relevance * frequency * priority
        # Clamp to 1-10 range
        score = novelty * relevance * frequency * priority
        return min(max(score, 1.0), 10.0)
