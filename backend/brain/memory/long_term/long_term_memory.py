import sqlite3
import os
from backend.utils.paths import get_db_path, ensure_dir

class LongTermMemory:
    def __init__(self, db_path=None):
        self.db_path = db_path or get_db_path("backend/storage/sqlite_db/memory.db")
        self._init_db()

    def _init_db(self):
        ensure_dir(self.db_path)
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        # Fix #6: Enforce WAL mode for concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS long_term_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                fact TEXT,
                importance INTEGER,
                access_count INTEGER DEFAULT 1,
                last_updated REAL,
                last_accessed REAL
            )
        ''')
        conn.commit()
        conn.close()

    def promote(self, user_id, event):
        # Fix #6: Use WAL and timeout
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute('''
            INSERT INTO long_term_facts (user_id, fact, importance, last_updated, last_accessed)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, event["content"], event["importance"], event["timestamp"], event["timestamp"]))
        conn.commit()
        conn.close()

    def get(self, user_id):
        import time
        from ...utils.decay_logic import DecayLogic
        
        # Fix #6: Use WAL and timeout
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute('''
            SELECT id, fact, importance, access_count, last_accessed FROM long_term_facts
            WHERE user_id = ?
        ''', (user_id,))
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            fid, fact, imp, count, last = row
            strength = DecayLogic.calculate_strength(imp, last, count)
            
            if strength > 1.0: # Retention threshold
                results.append({"fact": fact, "importance": imp, "strength": strength})
                # Reinforce
                cursor.execute('''
                    UPDATE long_term_facts SET access_count = access_count + 1, last_accessed = ?
                    WHERE id = ?
                ''', (time.time(), fid))
        
        conn.commit()
        conn.close()
        return sorted(results, key=lambda x: x["strength"], reverse=True)
