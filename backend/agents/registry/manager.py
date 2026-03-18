import sqlite3
import os
import time

class AgentRegistry:
    def __init__(self, db_path="backend/storage/agent_registry.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                agent_name TEXT,
                agent_role TEXT,
                capabilities TEXT,
                memory_access_level TEXT DEFAULT 'standard',
                created_at REAL
            )
        ''')
        # Insert default agent if not exists
        cursor.execute("SELECT agent_id FROM agents WHERE agent_id = 'default_agent'")
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO agents (agent_id, agent_name, agent_role, capabilities, memory_access_level, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ("default_agent", "Memoize Assistant", "assistant", "general", "full", time.time()))
        conn.commit()
        conn.close()

    def register_agent(self, agent_id, name, role, capabilities, access_level="standard"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO agents (agent_id, agent_name, agent_role, capabilities, memory_access_level, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (agent_id, name, role, capabilities, access_level, time.time()))
        conn.commit()
        conn.close()

    def get_agent(self, agent_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agents WHERE agent_id = ?", (agent_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "agent_id": row[0],
                "name": row[1],
                "role": row[2],
                "capabilities": row[3],
                "access_level": row[4],
                "created_at": row[5]
            }
        return None

    def list_agents(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agents")
        rows = cursor.fetchall()
        conn.close()
        return [{
            "agent_id": r[0],
            "name": r[1],
            "role": r[2],
            "capabilities": r[3],
            "access_level": r[4],
            "created_at": r[5]
        } for r in rows]
