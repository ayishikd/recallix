import sqlite3
import time

class TimelineEngine:
    def __init__(self, db_path="backend/storage/timeline_store/timeline.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                event_content TEXT,
                timestamp REAL
            )
        ''')
        conn.commit()
        conn.close()

    def append_event(self, user_id, content):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO events (user_id, event_content, timestamp)
            VALUES (?, ?, ?)
        ''', (user_id, content, time.time()))
        conn.commit()
        conn.close()

    def get_sequence(self, user_id, limit=50):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT event_content, timestamp FROM events
            WHERE user_id = ?
            ORDER BY timestamp ASC
            LIMIT ?
        ''', (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [{"content": row[0], "timestamp": row[1]} for row in rows]

    def detect_patterns(self, user_id):
        """
        Mock pattern detection.
        C++ Acceleration would handle complex sequence analysis.
        """
        events = self.get_sequence(user_id)
        if not events:
            return []
        # Example pattern: recurring keywords
        return ["recurring_topic_detected"]
