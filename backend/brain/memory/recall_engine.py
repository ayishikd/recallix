import json
import sqlite3
import time
import math
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

    def _calculate_unified_score(self, query, memory, semantic_score=None):
        """
        Fix #3: Unified Scoring Function
        semantic_similarity * 0.45 + lexical_overlap * 0.20 + importance * 0.20 + reinforcement * 0.10 + recency_decay * 0.05
        """
        content = memory.get("content", "").lower()
        q_lower = query.lower()
        
        # 1. Lexical Overlap (Simple Jaccard-ish)
        q_words = set(q_lower.split())
        c_words = set(content.split())
        overlap = len(q_words.intersection(c_words)) / max(len(q_words), 1)
        
        # 2. Importance (Scaled 0-1)
        importance = float(memory.get("importance", 5.0)) / 10.0
        
        # 3. Reinforcement (Scaled 0-1)
        reinforcement = float(memory.get("reinforcement_score", 1.0)) / 10.0
        
        # 4. Recency Decay (Exponential decay based on timestamp)
        # We assume timestamp is unix epoch. Half-life of 24 hours (86400s)
        ts = memory.get("timestamp", time.time())
        age = max(0, time.time() - ts)
        recency = math.exp(-age / 86400.0) 
        
        # 5. Semantic Score (provided by SemanticMemory if available)
        s_score = semantic_score if semantic_score is not None else 0.5
        
        final_score = (s_score * 0.45) + (overlap * 0.20) + (importance * 0.20) + (reinforcement * 0.10) + (recency * 0.05)
        return final_score

    def multi_stage_recall(self, user_id, query, agent_id="default_agent", top_k=5):
        # 0. Intent-Driven Retrieval Pipeline (Primary)
        if self.intent_manager:
            try:
                print(f"[RecallEngine] Intent-Driven Pipeline: {query[:40]}...")
                intent_results = self.intent_manager.execute_intent_recall(user_id, query, agent_id)
                memories = intent_results.get("memories", [])
                
                # Apply Unified Scoring
                for m in memories:
                    m["unified_score"] = self._calculate_unified_score(query, m)
                
                # Sort by unified score
                memories.sort(key=lambda x: x["unified_score"], reverse=True)

                # 4. Rerank for precision (Process full candidate pool)
                if self.reranker and memories:
                    print(f"[RecallEngine] Reranking {len(memories)} intent-results...")
                    # Take top 100 for reranking
                    candidates_to_rerank = memories[:100]
                    intent_results["memories"] = self.reranker.rerank(query, candidates_to_rerank, top_n=top_k)
                else:
                    intent_results["memories"] = memories[:top_k]
                
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
        
        # 2. Stage 1: Retrieval (Fetch more candidates)
        semantic_results = self.semantic.search(user_id, query, top_k=100) 
        episodic_candidates = self.episodic.search(user_id, query, agent_id=agent_id, limit=100)
        
        candidates = []
        seen = set()
        
        for c in semantic_results:
            if c.get("agent_id") == agent_id or c.get("memory_type") == "shared":
                sid = c.get("sqlite_id")
                if sid:
                    real_m = self.episodic.get_by_id(user_id, sid)
                    if real_m:
                        real_m["source"] = "semantic"
                        real_m["semantic_score"] = c.get("score", 0.5)
                        candidates.append(real_m)
                        seen.add(real_m["content"])
                else:
                    candidates.append({
                        "content": str(c.get("id")), 
                        "source": "semantic", 
                        "importance": c.get("importance", 5.0),
                        "semantic_score": c.get("score", 0.5)
                    })
                    seen.add(str(c.get("id")))
                
        for c in episodic_candidates:
            if c["content"] not in seen:
                c["source"] = "episodic"
                c["semantic_score"] = 0.5 # Baseline for purely lexical matches
                candidates.append(c)
                seen.add(c["content"])

        # Apply Unified Scoring to candidates
        for c in candidates:
            c["unified_score"] = self._calculate_unified_score(query, c, c.get("semantic_score"))
        
        candidates.sort(key=lambda x: x["unified_score"], reverse=True)

        # 3. Finalization logic (Rerank -> Attention)
        if self.reranker and candidates:
            print(f"[RecallEngine] Reranking {len(candidates)} candidates...")
            candidates = self.reranker.rerank(query, candidates[:100], top_n=top_k)

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
