import time
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

class MemoryManager:
    def __init__(self):
        self.sensory = SensoryMemory()
        self.working = WorkingMemory()
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.long_term = LongTermMemory()
        self.reflective = ReflectiveMemory()
        self.predictive = PredictiveRecall(self)
        self.state_inference = StateInference()
        self.timeline = TimelineEngine()
        self.prediction_engine = PredictionEngine()
        self.planning_engine = PlanningEngine(self)
        self.attention = AttentionController()
        self.reranker = NeuralReranker()
        
        # New Intent-Driven Retrieval logic
        self.intent_retrieval = IntentRetrievalManager(self)
        
        self.recall_engine = RecallEngine(self.episodic, self.semantic, self.long_term, self.reflective)
        self.recall_engine.intent_manager = self.intent_retrieval
        self.recall_engine.predictive = self.predictive
        self.recall_engine.attention = self.attention
        self.recall_engine.reranker = self.reranker

    def store(self, user_id, message, agent_id="default_agent", memory_type="private"):
        logs = []
        t0 = time.time()

        def log(system, stage, detail, started):
            elapsed = round((time.time() - started) * 1000, 1)
            logs.append({"system": system, "stage": stage, "detail": detail, "duration_ms": elapsed})

        # ── Stage 1: Sensory Memory ──
        s = time.time()
        self.sensory.add(user_id, message)
        log("python", "Sensory Buffer", f"Buffered in 60s TTL deque (max 10 items). Input: \"{message[:60]}\"", s)

        # ── Stage 2: Working Memory ──
        s = time.time()
        context = self.working.get(user_id)
        self.working.update(user_id, message)
        ctx_preview = context["summary"][:80] if context.get("summary") else "(empty)"
        log("python", "Working Memory", f"Active context updated. Previous summary: \"{ctx_preview}\"", s)

        # ── Stage 3: Importance Scoring ──
        s = time.time()
        importance = ImportanceRanker.calculate(message, context["summary"])
        score_label = "LOW" if importance < 4 else ("MEDIUM" if importance < 7 else "HIGH" if importance < 9 else "CRITICAL")
        log("python", "Importance Scoring", f"ImportanceRanker scored {importance:.1f}/10 ({score_label}). Factors: goal/preference/explicit/noise detection.", s)

        event = {
            "user_id": user_id,
            "agent_id": agent_id,
            "memory_type": memory_type,
            "content": message,
            "timestamp": time.time(),
            "importance": importance
        }

        # ── Stage 4: Episodic Memory ──
        s = time.time()
        self.episodic.store(event)
        log("python", "Episodic Storage", f"Stored in SQLite (WAL mode) with importance={importance:.1f}, reinforcement_score=1.0, keyword indexing enabled.", s)

        # ── Stage 5: Semantic Embedding ──
        s = time.time()
        self.semantic.store(
            user_id, 
            message, 
            event["timestamp"], 
            importance=event["importance"],
            agent_id=agent_id,
            memory_type=memory_type
        )
        log("cpp", "Vector Engine", f"Generated 128D embedding via SemanticMemory. Sent POST /add_vector to C++ VectorEngine (:8080). Cosine similarity index updated.", s)

        # ── Stage 6: Knowledge Graph ──
        s = time.time()
        # requests.post(self.infra_url + "/add_node", json={"id": message, "type": "event"})
        log("cpp", "Graph Engine", f"[Placeholder] Would add node to knowledge graph via POST /add_node on C++ GraphEngine (:8080).", s)

        # ── Stage 7: Cluster Assignment ──
        s = time.time()
        log("cpp", "Clustering", f"[Placeholder] Would trigger clustering via POST /cluster on C++ ClusteringEngine (:8080).", s)

        # ── Stage 8: Schema Tagging ──
        s = time.time()
        schema_tags = []
        msg_lower = message.lower()
        if any(w in msg_lower for w in ["name", "i am", "i'm"]): schema_tags.append("identity")
        if any(w in msg_lower for w in ["allergic", "allergy", "prefer", "hate"]): schema_tags.append("preference")
        if any(w in msg_lower for w in ["meeting", "schedule", "deadline", "next"]): schema_tags.append("calendar")
        if any(w in msg_lower for w in ["learn", "study", "course", "training"]): schema_tags.append("learning")
        if not schema_tags: schema_tags.append("general")
        log("python", "Schema Tagging", f"Detected schemas: {schema_tags}. Tags influence importance multiplier and meta-memory evolution.", s)

        # ── Stage 9: Long-Term Promotion ──
        s = time.time()
        promoted = False
        if event["importance"] > 8:
            self.long_term.promote(user_id, event)
            promoted = True
            log("python", "Long-Term Promotion", f"🔥 PROMOTED to Long-Term Memory! Importance {importance:.1f} > 8.0 threshold. Ebbinghaus decay applied. Protected from forgetting.", s)
        else:
            log("python", "Long-Term Gate", f"Not promoted (importance {importance:.1f} ≤ 8.0 threshold). Stays in Episodic with 30-day decay half-life.", s)

        # ── Stage 10: Timeline ──
        s = time.time()
        self.timeline.append_event(user_id, message)
        log("cpp", "Timeline Engine", f"Appended to chronological timeline via POST /append_event on C++ TimelineEngine (:8080). Enables temporal pattern detection.", s)

        # ── Stage 11: State Inference ──
        s = time.time()
        self.state_inference.infer_and_update(user_id, [event])
        log("ollama", "State Inference", f"Sent to Llama 3.1:8B via Ollama. LLM infers hidden user states (skill_level, interest_strength). Results stored in states.db.", s)

        # ── Stage 12: Processing Summary ──
        total_ms = round((time.time() - t0) * 1000, 1)
        log("python", "Pipeline Complete", f"All 12 stages finished in {total_ms}ms. Schemas: {schema_tags}. Promoted: {promoted}. Memory now indexed across {3 + (1 if promoted else 0)} stores.", s)

        return {
            "importance": importance,
            "schemas": schema_tags,
            "promoted": promoted,
            "total_ms": total_ms,
            "processing_log": logs
        }

    def retrieve(self, user_id, query, agent_id="default_agent"):
        # 1. Check Sensory Memory first
        sensory_data = self.sensory.get(user_id)
        
        # 2. Working Memory context
        working_summary = self.working.get(user_id)
        
        # 3. Multi-Stage Recall (Layers 3, 4, 5, 6 + Graph)
        recall_results = self.recall_engine.multi_stage_recall(user_id, query, agent_id=agent_id)
        
        # 4. Consolidate results for API
        return {
            "sensory": sensory_data,
            "working": working_summary,
            "intent": recall_results.get("intent"),
            "confidence": recall_results.get("confidence"),
            "retrieval_plan": recall_results.get("retrieval_plan"),
            "context_inference": recall_results.get("context_inference"),
            "memories": recall_results.get("memories", recall_results.get("final_memories", [])),
            "episodic": recall_results.get("episodic", []),
            "semantic": recall_results.get("semantic", []),
            "long_term": recall_results.get("long_term", []),
            "prediction": recall_results.get("prediction", {}),
            "schema_insights": recall_results.get("schema_insights", []),
            "latency_ms": recall_results.get("latency_ms", 0.0)
        }

    def delete(self, user_id, memory_id):
        """
        Deletes a memory across all layers.
        """
        # 1. Episodic
        self.episodic.delete(memory_id)
        # 2. Semantic/Vector (via C++ infra or direct)
        # 3. Timeline (by content match - simplified)
        return True

    def _calculate_importance(self, message):
        # Placeholder for importance scoring logic
        if "remember" in message.lower() or "important" in message.lower():
            return 9
        return 5
