import time
import sqlite3
from ..memory_ranking.importance_ranker import ImportanceRanker

class RankingWorker:
    def __init__(self, memory_manager):
        self.memory = memory_manager
        self.db_path = memory_manager.episodic.db_path

    def maintain_importance(self):
        """
        Periodically re-evaluates memory importance and handles promotions.
        """
        print("[RankingWorker] Maintaining memory rankings...")
        
        for _ in range(3):
            try:
                conn = sqlite3.connect(self.db_path, timeout=30)
                cursor = conn.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                
                # 1. Decay importance of existing memories
                cursor.execute("SELECT id, importance, last_accessed FROM episodic_events")
                rows = cursor.fetchall()
                
                for row in rows:
                    mem_id, base_imp, last_accessed = row
                    if last_accessed:
                        new_imp = ImportanceRanker.decay_importance(base_imp, last_accessed)
                        cursor.execute("UPDATE episodic_events SET importance = ? WHERE id = ?", (new_imp, mem_id))
                
                # 2. Promote highly important memories to Long Term
                cursor.execute("SELECT user_id, content, timestamp, importance FROM episodic_events WHERE importance > 9.0")
                to_promote = cursor.fetchall()
                
                for row in to_promote:
                    user_id, content, timestamp, importance = row
                    event = {
                        "user_id": user_id,
                        "content": content,
                        "timestamp": timestamp,
                        "importance": importance
                    }
                    self.memory.long_term.promote(user_id, event)
                    
                conn.commit()
                conn.close()
                print(f"[RankingWorker] Processed {len(rows)} memories.")
                return
            except sqlite3.OperationalError as e:
                print(f"[RankingWorker] DB locked, retrying... {e}")
                time.sleep(2)
