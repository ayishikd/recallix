import sqlite3
import os
import time
import json

class SchemaRegistry:
    def __init__(self, db_path="backend/storage/schema_registry/schemas.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evolved_schemas (
                schema_id TEXT PRIMARY KEY,
                schema_name TEXT,
                schema_fields TEXT,  -- JSON list of fields
                created_at REAL,
                confidence_score REAL,
                usage_frequency INTEGER DEFAULT 0,
                retrieval_success_rate REAL DEFAULT 1.0
            )
        ''')
        conn.commit()
        conn.close()

    def register_schema(self, schema_id, name, fields, confidence):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO evolved_schemas 
            (schema_id, schema_name, schema_fields, created_at, confidence_score)
            VALUES (?, ?, ?, ?, ?)
        ''', (schema_id, name, json.dumps(fields), time.time(), confidence))
        conn.commit()
        conn.close()

    def get_schema(self, schema_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM evolved_schemas WHERE schema_id = ?", (schema_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "schema_id": row[0],
                "name": row[1],
                "fields": json.loads(row[2]),
                "created_at": row[3],
                "confidence": row[4],
                "usage_frequency": row[5],
                "success_rate": row[6]
            }
        return None

    def list_schemas(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM evolved_schemas")
        rows = cursor.fetchall()
        conn.close()
        return [{
            "schema_id": r[0],
            "name": r[1],
            "fields": json.loads(r[2]),
            "created_at": r[3],
            "confidence": r[4],
            "usage": r[5],
            "success": r[6]
        } for r in rows]
