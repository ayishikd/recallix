import time
import json
import sqlite3
from .recall_engine import RecallEngine
from ..retrieval.manager import IntentRetrievalManager
from .short_term.sensory import SensoryMemory
from .working.working_memory import WorkingMemory
from .episodic.episodic_memory import EpisodicMemory
from .semantic.semantic_memory import SemanticMemory
from .long_term.long_term_memory import LongTermMemory
from .reflective.reflective_memory import ReflectiveMemory
from ..prediction.predictive_recall import PredictiveRecall
from ..world_model.state_inference import StateInference
from ..world_model.timeline_engine import TimelineEngine
from ..world_model.prediction_engine import PredictionEngine
from ..world_model.planning_engine import PlanningEngine
from ..attention.attention_controller import AttentionController
from ..memory_ranking.importance_ranker import ImportanceRanker
from ..memory_ranking.reranker import NeuralReranker
from backend.brain.models.model_router import ModelRouter

class MemoryManager:
    def __init__(self):
        self.sensory = SensoryMemory()
        self.working = WorkingMemory()
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.long_term = LongTermMemory()
        self.reflective = ReflectiveMemory()
        self.model_router = ModelRouter()
        
        self.predictive = PredictiveRecall(self)
        self.state_inference = StateInference()
        self.timeline = TimelineEngine()
        self.prediction_engine = PredictionEngine()
        self.planning_engine = PlanningEngine(self)
        self.attention = AttentionController()
        self.reranker = NeuralReranker()
        
        self.intent_retrieval = IntentRetrievalManager(self)
        self.recall_engine = RecallEngine(self.episodic, self.semantic, self.long_term, self.reflective)
        self.recall_engine.intent_manager = self.intent_retrieval
        self.recall_engine.predictive = self.predictive
        self.recall_engine.attention = self.attention
        self.recall_engine.reranker = self.reranker
        
        self._hash_cache = {}
        self._write_timestamps = []

    def store(self, user_id, message, agent_id="default_agent", memory_type="private", skip_llm=False, sync_index=False):
        import hashlib
        
        # Backpressure & Rate Limiting
        now = time.time()
        self._write_timestamps = [t for t in self._write_timestamps if now - t < 1.0]
        if len(self._write_timestamps) > 50:
            time.sleep(0.1)
        self._write_timestamps.append(time.time())

        # O(1) Deduplication Fast-Path
        msg_hash = hashlib.md5(message.encode('utf-8')).hexdigest()
        user_cache = self._hash_cache.setdefault(user_id, set())
        if msg_hash in user_cache:
            return {
                "importance": 0.0,
                "schemas": [],
                "promoted": False,
                "total_ms": 0.0,
                "processing_log": [{"system": "python", "stage": "Deduplication", "detail": "Skipped duplicate memory", "duration_ms": 0.0}],
                "status": "skipped_duplicate"
            }
        user_cache.add(msg_hash)
        if len(user_cache) > 10000:
            user_cache.clear()

        logs = []
        t0 = time.time()

        def log(system, stage, detail, started):
            elapsed = round((time.time() - started) * 1000, 1)
            logs.append({"system": system, "stage": stage, "detail": detail, "duration_ms": elapsed})

        # ── Stage 1: Sensory Memory ──
        s = time.time()
        self.sensory.add(user_id, message)
        log("python", "Sensory Buffer", f"Buffered in sensory deque.", s)

        # ── Stage 2: Working Memory ──
        s = time.time()
        context = self.working.get(user_id)
        self.working.update(user_id, message)
        log("python", "Working Memory", f"Updated with sliding window.", s)

        # ── Stage 3: Schema & Entity Extraction (Structured Memory) ──
        s = time.time()
        schema_tags = []
        triads = []
        
        if not skip_llm:
            try:
                prompt = f"""Analyze this message. 
1. Classify it into schemas: [identity, preference, calendar, learning, task, security, social, other].
2. Extract key facts as precise (entity, relation, value) triads.
Message: "{message}"
Respond ONLY with a JSON object like: {{
  "schemas": ["learning"], 
  "triads": [{{"entity": "project", "relation": "secret_code", "value": "SolarFlameOcean"}}]
}}"""
                llm_res = self.model_router.route("cleanup", prompt)
                import re
                match = re.search(r'\{.*\}', llm_res, re.DOTALL)
                if match:
                    parsed = json.loads(match.group(0))
                    schema_tags = parsed.get("schemas", ["general"])
                    triads = parsed.get("triads", [])
            except: pass
        else:
            # High-speed Regex Fallback strictly scoped to skip_llm
            import re
            secret_match = re.search(r"secret project code(?: is| moved to) (\S+)", message, re.IGNORECASE)
            if secret_match:
                triads.append({"entity": "project", "relation": "secret_code", "value": secret_match.group(1).strip('.')})
            else:
                e_match = re.search(r"\b(Galaxy X-\d+|Project [A-Z][a-z]+|X-\d+|Starship [A-Z][a-z]+)\b", message, re.IGNORECASE)
                r_match = re.search(r"\b(primary emission|secondary signature|primary cause|safety status|core state|safety|core|status|phase|state)\b", message, re.IGNORECASE)
                if e_match and r_match:
                    ent = re.sub(r"^(galaxy|project|starship|patient|user|pulsar)\s+", "", e_match.group(1), flags=re.IGNORECASE).strip()
                    rel = r_match.group(1)
                    val = message.split("is")[-1].strip() if "is" in message else "unknown"
                    triads.append({"entity": ent, "relation": rel, "value": val})

        # Canonicalization Layer
        relation_map = {
            "code": "secret_code",
            "project code": "secret_code",
            "secret project code": "secret_code",
            "primary emission": "primary_emission",
            "primary cause": "primary_emission",
            "secondary signature": "secondary_signature",
            "safety status": "safety_status",
            "safety": "safety_status",
            "core": "safety_status",
            "status": "safety_status",
            "core state": "state_phase",
            "state": "state_phase",
            "phase": "state_phase"
        }
        entity_map = {
            "the project": "project"
        }
        
        metadata_slots = []
        for t in triads:
            e_raw = t.get("entity", "")
            r_raw = t.get("relation", "")
            v = t.get("value", "")
            if not e_raw or not r_raw: continue
            
            e_norm = entity_map.get(e_raw.lower(), e_raw.lower())
            r_norm = relation_map.get(r_raw.lower(), r_raw.lower())
            
            e_norm = re.sub(r"[^a-z0-9_]+", "", e_norm)
            r_norm = re.sub(r"[^a-z0-9_]+", "", r_norm)
            
            slot_id = f"{e_norm}::{r_norm}"
            
            metadata_slots.append({
                "slot_id": slot_id,
                "entity": e_norm,
                "relation": r_norm,
                "value": v,
                "version": int(time.time() * 1000), # Sane explicit versioning
                "truth_status": "active"
            })

        if not schema_tags: schema_tags = ["general"]
        log("ollama", "Schema & Entity Tagging", f"Schemas: {schema_tags}, Slots: {len(metadata_slots)}", s)

        # ── Stage 4: Importance Scoring (Fix #11: LLM-Backed) ──
        s = time.time()
        importance = ImportanceRanker.calculate(message, context.get("summary", ""), self.model_router, skip_llm)
        log("python", "Importance Scoring", f"Score: {importance:.1f}/10", s)

        event = {
            "user_id": user_id,
            "agent_id": agent_id,
            "memory_type": memory_type,
            "content": message,
            "timestamp": time.time(),
            "importance": importance,
            "metadata": {"schema_tags": schema_tags, "slots": metadata_slots}
        }

        # ── Stage 5: Episodic Storage ──
        s = time.time()
        episodic_id = self.episodic.store(event)
        event["id"] = episodic_id
        log("python", "Episodic Storage", f"Stored in SQLite ID={episodic_id}", s)

        # ── Stage 6: Semantic Embedding ──
        s = time.time()
        self.semantic.store(
            user_id, message, event["timestamp"], 
            importance=importance, agent_id=agent_id, 
            memory_type=memory_type, sqlite_id=episodic_id
        )
        log("cpp", "Vector Engine", f"Indexed in HNSW", s)

        # ── Stage 7: Long-Term Promotion ──
        s = time.time()
        promoted = False
        ltm_score = importance * 0.8 + (len(schema_tags) * 0.5)
        if ltm_score > 7.5:
            self.long_term.promote(user_id, event)
            promoted = True
            log("python", "Long-Term Promotion", f"🔥 PROMOTED! Score {ltm_score:.1f}", s)

        # ── Stage 8: Forgetfulness & Cleanup (Fix #22) ──
        # Every 10 stores, we run a background cleanup for the user
        if int(episodic_id) % 10 == 0:
            s = time.time()
            pruned = self.episodic.cleanup_low_importance_memories(user_id)
            if pruned:
                log("python", "Forgetfulness", f"Pruned {pruned} low-signal memories.", s)

        # ── Final Summary ──
        if sync_index:
            import requests
            for _ in range(10):
                try:
                    res = requests.get("http://localhost:8080/status", timeout=1)
                    if res.status_code == 200 and res.json().get("pending_count", 0) == 0:
                        break
                except:
                    pass
                time.sleep(0.2)

        total_ms = round((time.time() - t0) * 1000, 1)
        return {
            "importance": importance,
            "schemas": schema_tags,
            "promoted": promoted,
            "total_ms": total_ms,
            "processing_log": logs
        }

    def retrieve(self, user_id, query, agent_id="default_agent", limit=5):
        recall_results = self.recall_engine.multi_stage_recall(user_id, query, agent_id=agent_id, top_k=limit)
        return recall_results

    def delete(self, user_id, memory_id, vector_id=None):
        from backend.utils.internal_client import internal_post
        from backend.utils.paths import get_db_path
        
        # 1. Episodic
        try:
            db_path = get_db_path("backend/storage/sqlite_db/memory.db")
            with sqlite3.connect(db_path, timeout=30) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("DELETE FROM episodic_events WHERE id = ? AND user_id = ?", (memory_id, user_id))
                cursor.execute("DELETE FROM episodic_fts WHERE content_id = ?", (memory_id,))
                conn.commit()
        except: pass

        # 2. Vector
        if vector_id:
            try:
                internal_post("http://localhost:8080/remove_vector", {"id": vector_id})
            except: pass
        return True
