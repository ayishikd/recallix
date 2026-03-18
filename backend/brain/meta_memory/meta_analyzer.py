import sqlite3
from collections import Counter
import re

class MetaAnalyzer:
    def __init__(self, timeline_db="backend/storage/timeline_store/timeline.db", reflections_db="backend/storage/sqlite_db/reflections.db"):
        self.timeline_db = timeline_db
        self.reflections_db = reflections_db

    def detect_patterns(self, user_id):
        """
        Scans timeline and reflections to find recurring themes.
        """
        timeline_events = self._get_timeline_events(user_id)
        reflections = self._get_reflections(user_id)
        
        # Simple keyword extraction and frequency analysis
        words = []
        for event in timeline_events:
            # Basic cleanup and tokenization
            clean_text = re.sub(r'[^\w\s]', '', event.lower())
            words.extend([w for w in clean_text.split() if len(w) > 4])
            
        for ref in reflections:
            clean_text = re.sub(r'[^\w\s]', '', ref.lower())
            words.extend([w for w in clean_text.split() if len(w) > 4])
            
        common_themes = Counter(words).most_common(5)
        
        patterns = []
        for word, count in common_themes:
            if count >= 3: # Threshold for a pattern
                patterns.append({
                    "theme": word,
                    "frequency": count,
                    "source": "multimodal_correlation"
                })
        
        return patterns

    def _get_timeline_events(self, user_id):
        try:
            conn = sqlite3.connect(self.timeline_db)
            cursor = conn.cursor()
            cursor.execute("SELECT event_content FROM events WHERE user_id = ?", (user_id,))
            rows = cursor.fetchall()
            conn.close()
            return [r[0] for r in rows]
        except:
            return []

    def _get_reflections(self, user_id):
        try:
            conn = sqlite3.connect(self.reflections_db)
            cursor = conn.cursor()
            cursor.execute("SELECT summary FROM reflections WHERE user_id = ?", (user_id,))
            rows = cursor.fetchall()
            conn.close()
            return [r[0] for r in rows]
        except:
            return []
