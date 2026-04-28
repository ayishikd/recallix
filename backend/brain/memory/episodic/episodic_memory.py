import sqlite3
import os
import time

class EpisodicMemory:
    def __init__(self, db_path="backend/storage/sqlite_db/memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path, timeout=60) # Increased timeout
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS episodic_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT DEFAULT 'default_agent',
                user_id TEXT,
                memory_type TEXT DEFAULT 'private',
                content TEXT,
                timestamp REAL,
                importance REAL,
                reinforcement_score REAL DEFAULT 1.0,
                retrieval_count INTEGER DEFAULT 0,
                last_used_timestamp REAL,
                access_count INTEGER DEFAULT 1,
                last_accessed REAL,
                cluster_id TEXT,
                schema_tags TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def store(self, event):
        # Using context manager for better lock handling
        try:
            with sqlite3.connect(self.db_path, timeout=60) as conn:
                conn.execute("PRAGMA journal_mode=WAL")
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO episodic_events (
                        agent_id, user_id, memory_type, content, timestamp, 
                        importance, last_accessed, cluster_id, schema_tags
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.get("agent_id", "default_agent"),
                    event["user_id"],
                    event.get("memory_type", "private"),
                    event["content"],
                    event["timestamp"],
                    event["importance"],
                    event["timestamp"],
                    event.get("cluster_id"),
                    event.get("schema_tags")
                ))
                return cursor.lastrowid
        except Exception as e:
            print(f"[Episodic] Critical Store Error: {e}")
        return None

    def get_by_id(self, user_id, memory_id):
        try:
            with sqlite3.connect(self.db_path, timeout=60) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, content, timestamp, importance, agent_id, memory_type FROM episodic_events WHERE id = ? AND user_id = ?", (memory_id, user_id))
                r = cursor.fetchone()
                if r:
                    return {"id": r[0], "content": r[1], "timestamp": r[2], "importance": r[3], "agent_id": r[4], "memory_type": r[5]}
        except: pass
        return None

    def search(self, user_id, query, agent_id="default_agent", limit=5):
        words = query.split()
        if not words: return []
        where_clause = " AND (" + " OR ".join(["content LIKE ?" for _ in words]) + ")"
        params = [user_id, agent_id] + [f"%{w}%" for w in words] + [limit]
        try:
            with sqlite3.connect(self.db_path, timeout=60) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT id, content, timestamp, importance, agent_id, memory_type FROM episodic_events WHERE user_id = ? AND (agent_id = ? OR memory_type = 'shared') {where_clause} ORDER BY timestamp DESC LIMIT ?", params)
                results = cursor.fetchall()
                return [{"id": r[0], "content": r[1], "timestamp": r[2], "importance": r[3], "agent_id": r[4], "memory_type": r[5]} for r in results]
        except: return []

    def get_by_timestamp(self, user_id, timestamp):
        try:
            with sqlite3.connect(self.db_path, timeout=60) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, content, timestamp, importance, agent_id, memory_type FROM episodic_events WHERE user_id = ? AND ABS(timestamp - ?) < 0.1 LIMIT 1", (user_id, float(timestamp)))
                r = cursor.fetchone()
                if r: return {"id": r[0], "content": r[1], "timestamp": r[2], "importance": r[3], "agent_id": r[4], "memory_type": r[5]}
        except: pass
        return None
