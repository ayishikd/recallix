import sqlite3
import os

class ArchiveStore:
    def __init__(self, db_path="backend/storage/archive_store/archived_memories.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS archived_memories (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                content TEXT,
                timestamp REAL,
                importance REAL,
                reinforcement_score REAL,
                schema_tags TEXT,
                archived_at REAL
            )
        ''')
        conn.commit()
        conn.close()

    def archive(self, memory):
        import time
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute('''
            INSERT OR REPLACE INTO archived_memories (id, user_id, content, timestamp, importance, reinforcement_score, schema_tags, archived_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            memory.get("id"),
            memory.get("user_id"),
            memory.get("content"),
            memory.get("timestamp"),
            memory.get("importance"),
            memory.get("reinforcement_score"),
            memory.get("schema_tags"),
            time.time()
        ))
        conn.commit()
        conn.close()
