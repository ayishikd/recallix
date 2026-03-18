import sqlite3
import time
import os
import json

class MetaMemoryEngine:
    def __init__(self, db_path="backend/storage/sqlite_db/meta_memory.db", registry_path="backend/storage/schema_registry.json"):
        self.db_path = db_path
        self.registry_path = registry_path
        self._init_db()
        self._init_registry()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meta_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meta_type TEXT,
                insight_text TEXT,
                confidence_score REAL,
                affected_component TEXT,
                created_timestamp REAL
            )
        ''')
        conn.commit()
        conn.close()

    def _init_registry(self):
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        if not os.path.exists(self.registry_path):
            with open(self.registry_path, 'w') as f:
                json.dump({"schemas": [], "version": 1.0}, f, indent=2)

    def store_insight(self, meta_type, insight_text, confidence, component):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO meta_insights (meta_type, insight_text, confidence_score, affected_component, created_timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (meta_type, insight_text, confidence, component, time.time()))
        conn.commit()
        conn.close()

    def get_latest_insights(self, limit=10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT meta_type, insight_text, confidence_score, affected_component, created_timestamp 
            FROM meta_insights 
            ORDER BY created_timestamp DESC 
            LIMIT ?
        ''', (limit,))
        results = cursor.fetchall()
        conn.close()
        return [
            {
                "meta_type": r[0],
                "insight_text": r[1],
                "confidence": r[2],
                "component": r[3],
                "timestamp": r[4]
            } for r in results
        ]
