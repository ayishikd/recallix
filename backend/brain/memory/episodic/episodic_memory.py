import sqlite3
import os
import time
from backend.utils.paths import get_db_path, ensure_dir
from backend.utils.internal_client import internal_post

class EpisodicMemory:
    def __init__(self, db_path=None):
        self.db_path = db_path or get_db_path("backend/storage/sqlite_db/memory.db")
        self._init_db()

    def _init_db(self):
        ensure_dir(self.db_path)
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        
        # Primary storage
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS episodic_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                agent_id TEXT,
                memory_type TEXT,
                content TEXT,
                timestamp REAL,
                importance REAL,
                reinforcement_score REAL DEFAULT 1.0,
                retrieval_count INTEGER DEFAULT 0
            )
        ''')
        
        # Fix #9: Use FTS5 for efficient lexical search
        cursor.execute("CREATE VIRTUAL TABLE IF NOT EXISTS episodic_fts USING fts5(content, content_id UNINDEXED)")
        
        conn.commit()
        conn.close()

    def store(self, event):
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        
        cursor.execute('''
            INSERT INTO episodic_events (user_id, agent_id, memory_type, content, timestamp, importance)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (event["user_id"], event["agent_id"], event["memory_type"], event["content"], event["timestamp"], event["importance"]))
        
        row_id = cursor.lastrowid
        
        # Sync with FTS5
        cursor.execute("INSERT INTO episodic_fts (content, content_id) VALUES (?, ?)", (event["content"], row_id))
        
        conn.commit()
        conn.close()
        return row_id

    def search(self, user_id, query, agent_id=None, limit=10):
        """
        Fix #9: Optimized hybrid search using FTS5 + Salience Ranking
        """
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        
        # Lexical search via FTS5
        fts_query = ' OR '.join(query.split())
        sql = '''
            SELECT e.* FROM episodic_events e
            JOIN episodic_fts f ON e.id = f.content_id
            WHERE e.user_id = ? AND f.content MATCH ?
        '''
        params = [user_id, fts_query]
        
        if agent_id:
            sql += " AND (e.agent_id = ? OR e.memory_type = 'shared')"
            params.append(agent_id)
            
        # Hybrid Ranking (Fix #3 from accuracy audit)
        sql += " ORDER BY (e.importance * 0.7 + e.reinforcement_score * 0.3) DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        results = []
        for r in rows:
            results.append({
                "id": r[0], "user_id": r[1], "agent_id": r[2],
                "memory_type": r[3], "content": r[4], "timestamp": r[5],
                "importance": r[6], "reinforcement_score": r[7]
            })
        conn.close()
        return results

    def get_by_id(self, user_id, memory_id):
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("SELECT * FROM episodic_events WHERE id = ? AND user_id = ?", (memory_id, user_id))
        r = cursor.fetchone()
        conn.close()
        if r:
            return {
                "id": r[0], "user_id": r[1], "agent_id": r[2],
                "memory_type": r[3], "content": r[4], "timestamp": r[5],
                "importance": r[6], "reinforcement_score": r[7]
            }
        return None
