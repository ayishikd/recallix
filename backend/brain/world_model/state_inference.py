import sqlite3
import time
from ..models.model_router import ModelRouter

class StateInference:
    def __init__(self, db_path="backend/storage/world_state_store/states.db"):
        self.db_path = db_path
        self.router = ModelRouter()
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
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
        conn.commit()
        conn.close()

    def infer_and_update(self, user_id, recent_memories):
        """
        Analyzes recent memories to infer hidden user states.
        """
        if not recent_memories:
            return

        context = "\n".join([m.get('content', '') for m in recent_memories])
        prompt = (
            f"Based on the following user interactions, infer the user's hidden states "
            f"(e.g., skill_level, interest_strength, topic_mastery). "
            f"Return the result as a list of key:value pairs.\n\n"
            f"Interactions:\n{context}"
        )

        inference_results = self.router.route("reasoning", prompt)
        
        # Simple parsing logic (assuming Key: Value format from LLM)
        lines = inference_results.strip().split('\n')
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                cursor.execute('''
                    INSERT INTO user_states (user_id, state_key, state_value, confidence, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(user_id, state_key) DO UPDATE SET
                        state_value = excluded.state_value,
                        confidence = excluded.confidence,
                        last_updated = excluded.last_updated
                ''', (user_id, key.strip(), value.strip(), 0.8, time.time()))
        
        conn.commit()
        conn.close()
        return inference_results

    def get_states(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT state_key, state_value, confidence FROM user_states WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return {row[0]: {"value": row[1], "confidence": row[2]} for row in rows}
