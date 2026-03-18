import time
import math

class ImportanceRanker:
    @staticmethod
    def calculate(content, context_summary, metadata=None):
        """
        Calculates intrinsic importance based on multiple cognitive factors.
        Returns a score between 1.0 and 10.0.
        """
        score = 5.0 # Base score
        
        content_lower = content.lower()
        
        # 1. Goal Detection (+3)
        goal_keywords = ["goal", "task", "need to", "must", "plan", "scheduled", "deadline"]
        if any(kw in content_lower for kw in goal_keywords):
            score += 3.0
            
        # 2. Preference Detection (+2)
        pref_keywords = ["like", "love", "hate", "prefer", "allergic", "interest"]
        if any(kw in content_lower for kw in pref_keywords):
            score += 2.0
            
        # 3. Explicit Importance (+4)
        if "important" in content_lower or "remember this" in content_lower:
            score += 4.0
            
        # 4. Small Talk / Noise (-3)
        small_talk = ["hello", "hi ", "how are you", "thanks", "bye", "okay"]
        if any(content_lower.startswith(st) for st in small_talk) or len(content_lower.split()) < 3:
            score -= 3.0
            
        # 5. Schema/Category Multipliers
        if metadata and metadata.get("schema_tags"):
            tags = metadata["schema_tags"]
            if "identity" in tags or "security" in tags:
                score *= 1.2
        
        # Clamp to 1.0 - 10.0
        return min(max(score, 1.0), 10.0)

    @staticmethod
    def decay_importance(base_score, last_accessed_time):
        """
        Calculate decayed importance over time if not accessed.
        """
        elapsed_days = (time.time() - last_accessed_time) / 86400
        # Half-life of 30 days for importance
        decay_factor = math.pow(0.5, elapsed_days / 30)
        return base_score * decay_factor
