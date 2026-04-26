import os
import sqlite3

DB_PATHS = [
    "backend/storage/sqlite_db/memory.db",
    "backend/storage/world_state_store/states.db",
    "backend/storage/timeline_store/timeline.db",
    "backend/storage/schema_registry/schemas.db",
    "backend/storage/agent_registry.db",
    "backend/storage/sqlite_db/reflections.db"
]

def init():
    for path in DB_PATHS:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        if "memory.db" in path:
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
        elif "states.db" in path:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    state_key TEXT,
                    state_value TEXT,
                    confidence REAL,
                    last_updated REAL,
                    UNIQUE(user_id, state_key)
                )
            ''')
        elif "timeline.db" in path:
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
        print(f"Initialized {path}")

if __name__ == "__main__":
    init()
