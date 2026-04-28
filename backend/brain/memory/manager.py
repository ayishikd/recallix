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

    def store(self, user_id, message, agent_id="default_agent", memory_type="private", skip_llm=False):
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
        entities = []
        relations = []
        if not skip_llm:
            try:
                prompt = f"""Analyze this message. 
1. Classify it into schemas: [identity, preference, calendar, learning, task, security, social, other].
2. Extract key entities (galaxy, project, person, etc.) and their relations.
Message: "{message}"
Respond ONLY with a JSON object like: {{
  "schemas": ["learning"], 
  "entities": [{{"type": "galaxy", "id": "X-35"}}],
  "relations": [{{"subject": "X-35", "type": "primary_emission", "object": "synchrotron"}}]
}}"""
                llm_res = self.model_router.route("cleanup", prompt)
                import re
                match = re.search(r'\{.*\}', llm_res, re.DOTALL)
                if match:
                    parsed = json.loads(match.group(0))
                    schema_tags = parsed.get("schemas", ["general"])
                    entities = parsed.get("entities", [])
                    relations = parsed.get("relations", [])
            except: pass
        else:
            # High-speed Regex Fallback for symbolic facts (Fix #25)
            import re
            e_match = re.search(r"\b(Galaxy X-\d+|Project [A-Z][a-z]+)\b", message, re.IGNORECASE)
            if e_match:
                entities = [{"type": "symbolic", "id": e_match.group(1)}]
            
            r_match = re.search(r"\b(primary emission|status|location|security|primary cause)\b", message, re.IGNORECASE)
            if r_match:
                norm_rel = r_match.group(1).lower().replace(" ", "_")
                relations = [{"type": norm_rel}]

        if not schema_tags: schema_tags = ["general"]
        log("ollama", "Schema & Entity Tagging", f"Schemas: {schema_tags}, Entities: {entities}", s)

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
            "metadata": {"schema_tags": schema_tags, "entities": entities, "relations": relations}
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
        total_ms = round((time.time() - t0) * 1000, 1)
        return {
            "importance": importance,
            "schemas": schema_tags,
            "promoted": promoted,
            "total_ms": total_ms,
            "processing_log": logs
        }

    def retrieve(self, user_id, query, agent_id="default_agent"):
        recall_results = self.recall_engine.multi_stage_recall(user_id, query, agent_id=agent_id)
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
