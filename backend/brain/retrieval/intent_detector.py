import re
import time
from functools import lru_cache

class IntentDetector:
    def __init__(self):
        # Intent mappings as per requirements + conversational refinement
        self.rules = {
            "conversation": [r"\bhey\b", r"\bhello\b", r"\bhi\b", r"how\sare\syou", r"how\'s\sit\sgoing", r"\bthanks\b", r"\bgood\smorning\b"],
            "learning": [r"\bhow\s(do|can|to|does|is|are)\b", r"\bwhy\b", r"\bexplain\b", r"\bwhat\sis\b"],
            "task_execution": [r"\bplan\b", r"\bbuild\b", r"\bcreate\b", r"\bexecute\b"],
            "memory_store": [r"\bremember\b", r"\bnote\b", r"\bsave\b"],
            "preference_update": [r"\blike\b", r"\bdislike\b", r"\bprefer\b", r"\bhate\b", r"\blove\b"],
            "research": [r"\bcompare\b", r"\banalyze\b", r"\bresearch\b"]
        }

    @lru_cache(maxsize=1024)
    def detect(self, query):
        """
        Classifies user queries into intent categories.
        Fix #2: Using lru_cache to prevent memory leaks while maintaining performance.
        """
        query_lower = query.lower()
        
        # Priority 1: Check Conversation first
        for pattern in self.rules["conversation"]:
            if re.search(pattern, query_lower):
                return {"intent": "conversation", "confidence": 0.9}

        detected_intent = "conversation" # Default fallback
        max_matches = 0
        
        # Priority 2: Check other intents
        for intent in ["learning", "task_execution", "memory_store", "preference_update", "research"]:
            patterns = self.rules[intent]
            matches = 0
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    matches += 1
            
            if matches > max_matches:
                max_matches = matches
                detected_intent = intent
                
        # Simple confidence logic
        confidence = 0.5 if max_matches == 0 else min(0.6 + (max_matches * 0.1), 0.95)
        
        return {
            "intent": detected_intent,
            "confidence": confidence
        }
