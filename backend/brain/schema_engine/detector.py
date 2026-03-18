from collections import Counter
import re

class PatternDetector:
    def __init__(self, min_occurrence=3):
        self.min_occurrence = min_occurrence

    def detect_patterns(self, memories):
        """
        Detects recurring themes in a list of memory contents.
        Uses a simplified keyword-frequency clustering approach.
        """
        if not memories:
            return []

        # 1. Clean and tokenize
        all_words = []
        for m in memories:
            text = m["content"].lower()
            words = re.findall(r'\w+', text)
            # Remove common stop words (simplified)
            stop_words = {"i", "am", "is", "a", "the", "to", "and", "in", "it", "my", "of"}
            filtered = [w for w in words if w not in stop_words and len(w) > 2]
            all_words.extend(filtered)

        # 2. Count frequencies
        counts = Counter(all_words)
        
        # 3. Identify potential pattern candidates (words occurring > min_occurrence)
        candidates = [word for word, count in counts.items() if count >= self.min_occurrence]
        
        # 4. Group memories by candidates
        clusters = {}
        for cand in candidates:
            matching_memories = [m for m in memories if cand in m["content"].lower()]
            if len(matching_memories) >= self.min_occurrence:
                clusters[cand] = {
                    "pattern": cand,
                    "count": len(matching_memories),
                    "memories": matching_memories
                }

        return list(clusters.values())
