import sqlite3
import os
import time

class EpisodicMemory:
    def __init__(self, db_path="backend/storage/sqlite_db/memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
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
        
        # Migration: Add agent_id if it doesn't exist
        cursor.execute("PRAGMA table_info(episodic_events)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'agent_id' not in columns:
            cursor.execute("ALTER TABLE episodic_events ADD COLUMN agent_id TEXT DEFAULT 'default_agent'")
        if 'memory_type' not in columns:
            cursor.execute("ALTER TABLE episodic_events ADD COLUMN memory_type TEXT DEFAULT 'private'")
            
        conn.commit()
        conn.close()

    def store(self, event):
        for _ in range(5):
            try:
                conn = sqlite3.connect(self.db_path, timeout=30)
                cursor = conn.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
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
                conn.commit()
                conn.close()
                return
            except sqlite3.OperationalError as e:
                print(f"[Episodic] DB locked during store, retrying... {e}")
                time.sleep(1)

    def search(self, user_id, query, agent_id="default_agent", limit=5):
        # Improved: search for any of the keywords
        words = query.split()
        if not words:
            return []
            
        # Logic: (agent's private memories OR any shared memory) AND keyword match
        where_clause = " AND (" + " OR ".join(["content LIKE ?" for _ in words]) + ")"
        params = [user_id, agent_id] + [f"%{w}%" for w in words] + [limit]
        
        for _ in range(5):
            try:
                conn = sqlite3.connect(self.db_path, timeout=30)
                cursor = conn.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                # Updated SQL to handle agent/shared logic
                cursor.execute(f'''
                    SELECT id, content, timestamp, importance, cluster_id, schema_tags, reinforcement_score, agent_id, memory_type
                    FROM episodic_events
                    WHERE user_id = ? 
                    AND (agent_id = ? OR memory_type = 'shared')
                    {where_clause}
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', params)
                results = cursor.fetchall()
                
                # Update access count
                if results:
                    cursor.execute(f'''
                        UPDATE episodic_events 
                        SET access_count = access_count + 1, last_accessed = ?
                        WHERE user_id = ? 
                        AND (agent_id = ? OR memory_type = 'shared')
                        {where_clause}
                    ''', [time.time(), user_id, agent_id] + [f"%{w}%" for w in words])
                    conn.commit()
                    
                conn.close()
                return [
                    {
                        "id": r[0], "content": r[1], "timestamp": r[2], 
                        "importance": r[3], "cluster_id": r[4], 
                        "schema_tags": r[5], "reinforcement_score": r[6],
                        "agent_id": r[7], "memory_type": r[8]
                    } for r in results
                ]
            except sqlite3.OperationalError as e:
                print(f"[Episodic] DB locked during search, retrying... {e}")
                time.sleep(1)
        return []

    def list_all(self, limit=100):
        for _ in range(5):
            try:
                conn = sqlite3.connect(self.db_path, timeout=30)
                cursor = conn.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                # Removed user_id filter for worker bulk access
                cursor.execute('''
                    SELECT id, content, timestamp, importance, cluster_id, schema_tags, reinforcement_score, agent_id, memory_type
                    FROM episodic_events
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
                results = cursor.fetchall()
                conn.close()
                return [
                    {
                        "id": r[0], "content": r[1], "timestamp": r[2], 
                        "importance": r[3], "cluster_id": r[4], 
                        "schema_tags": r[5], "reinforcement_score": r[6],
                        "agent_id": r[7], "memory_type": r[8]
                    } for r in results
                ]
            except sqlite3.OperationalError as e:
                print(f"[Episodic] DB locked during list_all, retrying... {e}")
                time.sleep(1)
        return []
