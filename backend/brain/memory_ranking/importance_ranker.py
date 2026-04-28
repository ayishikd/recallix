import time
import math
import json

class ImportanceRanker:
    @staticmethod
    def calculate(content, context_summary, model_router=None, skip_llm=False):
        """
        Calculates intrinsic importance. 
        Fix #11: Uses LLM-backed scoring when available, with heuristic fallback.
        """
        # 1. Heuristic Base
        score = 5.0
        content_lower = content.lower()
        
        goal_keywords = ["goal", "task", "need to", "must", "plan", "scheduled", "deadline"]
        if any(kw in content_lower for kw in goal_keywords): score += 2.0
            
        pref_keywords = ["like", "love", "hate", "prefer", "allergic", "interest"]
        if any(kw in content_lower for kw in pref_keywords): score += 1.5
            
        if "important" in content_lower or "remember this" in content_lower: score += 3.0
            
        small_talk = ["hello", "hi ", "how are you", "thanks", "bye", "okay"]
        if any(content_lower.startswith(st) for st in small_talk) or len(content_lower.split()) < 3:
            score -= 3.0

        # 2. LLM Refinement (Fix #11)
        if not skip_llm and model_router:
            try:
                # Use a fast classification prompt
                prompt = f"""Rate the importance of this message for long-term memory (1-10).
Message: "{content}"
Context: "{context_summary[:200]}"
Respond ONLY with a JSON object like {{"score": 7.5, "reason": "..."}}"""
                
                llm_res = model_router.fast_model(prompt)
                if llm_res:
                    # Basic JSON extraction
                    import re
                    match = re.search(r'\{.*\}', llm_res, re.DOTALL)
                    if match:
                        data = json.loads(match.group(0))
                        llm_score = float(data.get("score", 5.0))
                        # Blend heuristic and LLM (60% weight to LLM)
                        score = (score * 0.4) + (llm_score * 0.6)
            except Exception as e:
                print(f"[ImportanceRanker] LLM scoring failed: {e}")

        return min(max(score, 1.0), 10.0)

    @staticmethod
    def decay_importance(base_score, last_accessed_time):
        elapsed_days = (time.time() - last_accessed_time) / 86400
        decay_factor = math.pow(0.5, elapsed_days / 30)
        return base_score * decay_factor
