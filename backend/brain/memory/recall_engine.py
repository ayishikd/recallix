import json
import sqlite3
import time
from ..prediction.predictive_recall import PredictiveRecall
from ..schema_engine.registry.manager import SchemaRegistry
from ..retrieval.manager import IntentRetrievalManager

class RecallEngine:
    def __init__(self, episodic, semantic, long_term, reflective, graph_infra_url="http://localhost:8080"):
        self.episodic = episodic
        self.semantic = semantic
        self.long_term = long_term
        self.reflective = reflective
        self.graph_url = graph_infra_url
        self.schema_registry = SchemaRegistry()
        
        # Intent-driven manager (initialized via MemoryManager)
        self.intent_manager = None 
        
        # Predictive and attention modules
        self.predictive = None 
        self.attention = None 
        self.reranker = None 

    def multi_stage_recall(self, user_id, query, agent_id="default_agent", top_k=5):
        """
        Main entry point for memory recall. 
        Uses Intent-Driven Retrieval as the primary path.
        """
        # 0. Intent-Driven Retrieval Pipeline (Primary)
        if self.intent_manager:
            try:
                print(f"[RecallEngine] Intent-Driven Pipeline: {query[:40]}...")
                intent_results = self.intent_manager.execute_intent_recall(user_id, query, agent_id)
                
                # 4. Rerank for precision
                if self.reranker and intent_results.get("memories"):
                    print(f"[RecallEngine] Reranking {len(intent_results['memories'])} intent-results...")
                    intent_results["memories"] = self.reranker.rerank(query, intent_results["memories"], top_n=top_k)
                
                # Apply reinforcement
                self._reinforce_memories(user_id, intent_results["memories"])
                
                # Combine with schema insights
                intent_results["schema_insights"] = self._get_schema_insights(query)
                return intent_results
            except Exception as e:
                print(f"[RecallEngine] Intent Retrieval failed, falling back: {e}")

        # 1. Fallback: Standard Pipeline
        return self._legacy_recall(user_id, query, agent_id, top_k)

    def _legacy_recall(self, user_id, query, agent_id, top_k):
        # 1. Predictive Signals
        prediction = {}
        if self.predictive:
             prediction = self.predictive.preload_context(user_id, query)
        
        # 2. Stage 1: Retrieval
        semantic_results = self.semantic.search(user_id, query, top_k=20) 
        episodic_candidates = self.episodic.search(user_id, query, agent_id=agent_id, limit=20)
        
        candidates = []
        seen = set()
        
        for c in semantic_results:
            if c.get("agent_id") == agent_id or c.get("memory_type") == "shared":
                # Fetch real content from episodic for the reranker to work!
                sid = c.get("sqlite_id")
                if sid:
                    real_m = self.episodic.get_by_id(user_id, sid)
                    if real_m:
                        real_m["source"] = "semantic"
                        candidates.append(real_m)
                        seen.add(real_m["content"])
                else:
                    candidates.append({"content": str(c.get("id")), "source": "semantic", "importance": 5.0})
                    seen.add(str(c.get("id")))
                
        for c in episodic_candidates:
            if c["content"] not in seen:
                c["source"] = "episodic"
                candidates.append(c)
                seen.add(c["content"])

        # 3. Finalization logic (Rerank -> Attention)
        if self.reranker and candidates:
            print(f"[RecallEngine] Reranking {len(candidates)} candidates...")
            candidates = self.reranker.rerank(query, candidates, top_n=20)

        final_memories = candidates[:top_k]
        if self.attention and candidates:
            scored = self.attention.score_memories(candidates, prediction)
            final_memories = self.attention.filter(scored, top_n=top_k)

        return {
            "intent": "legacy_fallback",
            "memories": final_memories,
            "schema_insights": self._get_schema_insights(query)
        }

    def _get_schema_insights(self, query):
        schemas = self.schema_registry.list_schemas()
        relevant = []
        q_lower = query.lower()
        for s in schemas:
            if s["name"].lower() in q_lower or any(f.lower() in q_lower for f in s["fields"]):
                relevant.append(s)
        return relevant

    def _reinforce_memories(self, user_id, memories_list):
        from ..memory_ranking.reinforcement_learning import MemoryRL
        rl = MemoryRL()
        db_path = "backend/storage/sqlite_db/memory.db"
        try:
            conn = sqlite3.connect(db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            for m in memories_list:
                # Handle different formats (builder output vs raw dict)
                metadata = m.get("metadata", {}) if isinstance(m, dict) else {}
                m_id = metadata.get("id") or m.get("id")
                if m_id:
                    cursor.execute("SELECT reinforcement_score FROM episodic_events WHERE id = ?", (m_id,))
                    row = cursor.fetchone()
                    if row:
                        new_score = rl.reinforce_positive(row[0])
                        cursor.execute('''
                            UPDATE episodic_events SET reinforcement_score = ?, retrieval_count = retrieval_count + 1 
                            WHERE id = ?
                        ''', (new_score, m_id))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[RecallEngine] Reinforcement error: {e}")
