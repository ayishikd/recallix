import sqlite3
import time
import requests
import os
from ..memory.archive.archive_store import ArchiveStore
from ..memory_ranking.reinforcement_learning import MemoryRL

class ForgettingWorker:
    def __init__(self, memory_manager, db_path="backend/storage/sqlite_db/memory.db", infra_url="http://localhost:8080"):
        self.memory = memory_manager
        self.db_path = db_path
        self.infra_url = infra_url
        self.archive_store = ArchiveStore()
        self.rl = MemoryRL()

    def run_cleanup(self):
        """
        Periodically scan episodic memory and apply forgetting policies.
        """
        if not os.path.exists(self.db_path):
            return

        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        
        # Get all memories
        cursor.execute('''
            SELECT id, user_id, content, timestamp, importance, reinforcement_score, schema_tags 
            FROM episodic_events
        ''')
        memories = cursor.fetchall()
        
        now = time.time()
        for m in memories:
            m_dict = {
                "id": m[0],
                "user_id": m[1],
                "content": m[2],
                "timestamp": m[3],
                "importance": m[4],
                "reinforcement_score": m[5],
                "schema_tags": m[6]
            }
            
            age_days = (now - m_dict["timestamp"]) / (24 * 3600)
            value = self.rl.calculate_value(m_dict["importance"], m_dict["reinforcement_score"])
            
            action = self.rl.get_policy(value, m_dict["importance"], age_days)
            print(f"[Forgetting] Evaluating: {m_dict['content'][:20]}... | Imp: {m_dict['importance']} | Val: {value:.2f} | Age: {age_days:.1f}d | Action: {action}")
            
            if action == "delete":
                print(f"[Forgetting] Deleting low-value memory: {m_dict['id']}")
                self._atomic_delete(m_dict)
            elif action == "archive":
                print(f"[Forgetting] Archiving memory: {m_dict['id']}")
                self.archive_store.archive(m_dict)
                self._atomic_delete(m_dict)
            elif action == "protect":
                # Maybe tag as protected in DB if not already?
                pass
                
        conn.close()

    def _atomic_delete(self, memory):
        """
        Removes memory from SQLite, Vector, Graph, and Timeline.
        """
        # 1. Remove from SQLite (Episodic)
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM episodic_events WHERE id = ?", (memory["id"],))
        conn.commit()
        conn.close()
        
        # 2. Remove from Vector Engine
        mem_id = f"{memory['user_id']}_{memory['timestamp']}"
        try:
            requests.post(f"{self.infra_url}/remove_vector", json={"id": mem_id})
        except Exception as e:
            print(f"[Forgetting] Vector deletion error: {e}")
            
        # 3. Remove from Graph Engine
        try:
            requests.post(f"{self.infra_url}/remove_node", json={"id": memory['content']})
        except Exception as e:
            print(f"[Forgetting] Graph deletion error: {e}")
            
        # 4. Remove from Timeline Engine
        try:
            requests.post(f"{self.infra_url}/remove_timeline_event", json={
                "user_id": memory['user_id'],
                "content": memory['content']
            })
        except Exception as e:
            print(f"[Forgetting] Timeline deletion error: {e}")
            
        # 5. Semantic Memory also needs to be updated if it maintains local state (it doesn't currently)
        pass
