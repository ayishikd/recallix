import sqlite3
import os
import time
import json
import re
from backend.utils.paths import get_db_path, ensure_dir
from backend.utils.internal_client import internal_post

class EpisodicMemory:
    def __init__(self, db_path=None):
        from backend.utils.paths import get_db_path, ensure_dir
        self.db_path = db_path or get_db_path("backend/storage/sqlite_db/memory.db")
        ensure_dir(os.path.dirname(self.db_path))
        
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        
        # Kernel v2 Schema: Supporting versioned truth states
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS episodic_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                agent_id TEXT,
                memory_type TEXT,
                content TEXT,
                timestamp REAL,
                importance REAL DEFAULT 5.0,
                reinforcement_score REAL DEFAULT 1.0,
                retrieval_count INTEGER DEFAULT 0,
                metadata TEXT,
                entity_id TEXT,
                relation_type TEXT,
                status TEXT DEFAULT 'ACTIVE'
            )
        ''')
        
        cursor.execute("CREATE VIRTUAL TABLE IF NOT EXISTS episodic_fts USING fts5(content, content_id UNINDEXED, user_id UNINDEXED)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_relation_status ON episodic_events(entity_id, relation_type, status)")
        
        conn.commit()
        conn.close()

    def store(self, event):
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        
        user_id = event["user_id"]
        content = event["content"]
        timestamp = event.get("timestamp", time.time())
        metadata = event.get("metadata", {})
        
        # Kernel v2: Extract symbolic keys for state tracking
        entity_id = None
        relation_type = None
        if metadata:
            entities = metadata.get("entities", [])
            relations = metadata.get("relations", [])
            if entities:
                entity_id = str(entities[0].get("id") if isinstance(entities[0], dict) else entities[0]).lower()
            if relations:
                relation_type = str(relations[0].get("type") if isinstance(relations[0], dict) else relations[0]).lower()

        # 1. State Suppression: Mark previous versions as OBSOLETE
        if entity_id and relation_type:
            cursor.execute("""
                UPDATE episodic_events 
                SET status = 'OBSOLETE' 
                WHERE user_id = ? AND entity_id = ? AND relation_type = ? AND status = 'ACTIVE'
            """, (user_id, entity_id, relation_type))

        # 2. Store new state
        cursor.execute("""
            INSERT INTO episodic_events 
            (user_id, agent_id, memory_type, content, timestamp, importance, reinforcement_score, retrieval_count, metadata, entity_id, relation_type, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, 'ACTIVE')
        """, (
            user_id, event.get("agent_id", "default"), event.get("memory_type", "private"),
            content, timestamp, event.get("importance", 5.0), 
            event.get("reinforcement_score", 1.0), json.dumps(metadata),
            entity_id, relation_type
        ))
        
        memory_id = cursor.lastrowid
        cursor.execute("INSERT INTO episodic_fts (content_id, content, user_id) VALUES (?, ?, ?)", (memory_id, content, user_id))
        conn.commit()
        conn.close()
        return memory_id

    def search(self, user_id, query, agent_id=None, limit=10, include_obsolete=False):
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        
        # 1. Identify query entities for targeted indexing
        entity_list = re.findall(r"\bGalaxy X-\d+\b|\bProject [A-Z][a-z]+\b|\bID[:\s]\d+\b|\b[A-Z]{2,}-\d+\b", query, re.IGNORECASE)
        
        if entity_list:
            # Broad search for entity components
            entity_tokens = []
            for e in entity_list:
                clean_e = re.sub(r"[^a-zA-Z0-9]+", " ", e).strip()
                if clean_e:
                    entity_tokens.append(f"({clean_e})")
            fts_query = ' OR '.join(entity_tokens)
        else:
            tokens = [f'"{w}"' for w in query.replace('"', '').split() if len(w) > 2]
            fts_query = ' OR '.join(tokens) if tokens else "*"

        # Kernel v2: Filter for ACTIVE status unless explicit history requested
        status_filter = "AND e.status = 'ACTIVE'" if not include_obsolete else ""
        
        sql = f"""
            SELECT e.*, f.bm25_score 
            FROM episodic_events e
            JOIN (SELECT content_id, bm25(episodic_fts) as bm25_score FROM episodic_fts WHERE episodic_fts MATCH ? AND user_id = ?) f
            ON e.id = f.content_id
            WHERE e.user_id = ? {status_filter}
        """
        params = [fts_query, user_id, user_id]
        
        print(f"🔍 [EpisodicSearch] SQL: {sql}")
        print(f"🔍 [EpisodicSearch] Params: {params}")
        
        if agent_id:
            sql += " AND (e.agent_id = ? OR e.memory_type = 'shared')"
            params.append(agent_id)
            
        sql += " ORDER BY bm25_score ASC LIMIT ?" # bm25() returns negative values (more negative = better match)
        params.append(limit)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        results = []
        for r in rows:
            # Kernel v2: Index 13 is bm25_score (after id, user, agent, type, content, ts, imp, reinf, count, meta, ent, rel, status)
            raw_bm25 = r[13]
            bm25_positive = abs(raw_bm25) if raw_bm25 else 0.0
            
            results.append({
                "id": r[0], "user_id": r[1], "agent_id": r[2],
                "memory_type": r[3], "content": r[4], "timestamp": r[5],
                "importance": r[6], "reinforcement_score": r[7],
                "metadata": r[9],
                "entity_id": r[10], "relation_type": r[11], "status": r[12],
                "bm25_score": bm25_positive
            })
        conn.close()
        return results

    def cleanup_low_importance_memories(self, user_id, age_days=7):
        """
        Prune 'Low-Signal' memories: Low importance AND never retrieved.
        """
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        
        # Threshold: Importance < 3 and Retrieval Count == 0
        cutoff = time.time() - (age_days * 86400)
        
        # 1. Find victims
        cursor.execute("""
            SELECT id FROM episodic_events 
            WHERE user_id = ? AND importance < 3.0 AND retrieval_count = 0 AND timestamp < ?
        """, (user_id, cutoff))
        victims = [r[0] for r in cursor.fetchall()]
        
        if victims:
            print(f"[EpisodicMemory] 🧹 Pruning {len(victims)} low-signal memories for {user_id}")
            placeholders = ','.join(['?'] * len(victims))
            cursor.execute(f"DELETE FROM episodic_events WHERE id IN ({placeholders})", victims)
            cursor.execute(f"DELETE FROM episodic_fts WHERE content_id IN ({placeholders})", victims)
            conn.commit()
            cursor.execute("PRAGMA wal_checkpoint(PASSIVE)")
            
        conn.close()
        return len(victims)

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
                "importance": r[6], "reinforcement_score": r[7],
                "metadata": r[9] # r[8] is retrieval_count
            }
        return None
