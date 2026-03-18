import sqlite3
import time

class ReflectiveMemory:
    def __init__(self, db_path="backend/storage/sqlite_db/reflections.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reflections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                summary TEXT,
                source_memories TEXT,
                confidence REAL,
                timestamp REAL
            )
        ''')
        conn.commit()
        conn.close()

    def store_reflection(self, user_id, summary, source_ids, confidence):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reflections (user_id, summary, source_memories, confidence, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, summary, ",".join(map(str, source_ids)), confidence, time.time()))
        conn.commit()
        conn.close()

    def get_reflections(self, user_id, limit=5):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT summary, confidence, timestamp FROM reflections
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        results = cursor.fetchall()
        conn.close()
        return [{"summary": r[0], "confidence": r[1], "timestamp": r[2]} for r in results]
