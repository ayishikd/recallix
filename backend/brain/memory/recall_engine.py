import json
import sqlite3
import time
import math
import re
from ..prediction.predictive_recall import PredictiveRecall
from ..schema_engine.registry.manager import SchemaRegistry
from ..retrieval.manager import IntentRetrievalManager
from .scorers import (
    SemanticScorer, LexicalScorer, EntityScorer, 
    RelationScorer, SalienceScorer, TemporalScorer
)

class RecallEngine:
    def __init__(self, episodic, semantic, long_term, reflective, graph_infra_url="http://localhost:8080"):
        self.episodic = episodic
        self.semantic = semantic
        self.long_term = long_term
        self.reflective = reflective
        self.graph_url = graph_infra_url
        self.schema_registry = SchemaRegistry()
        
        # Modular Scorers
        self.scorers = {
            "semantic": SemanticScorer(),
            "lexical": LexicalScorer(),
            "entity": EntityScorer(),
            "relation": RelationScorer(),
            "salience": SalienceScorer(),
            "temporal": TemporalScorer()
        }
        
        self.intent_manager = None 
        self.predictive = None 
        self.attention = None 
        self.reranker = None 

    def _classify_query(self, query):
        q_lower = query.lower()
        symbolic_triggers = ["what is", "who is", "name", "id", "code", "deadline", "date", "when", "where", "project", "number"]
        identity_triggers = ["my name", "i am", "who am i", "my cat", "my dog", "my preference", "i like"]
        
        if any(t in q_lower for t in identity_triggers):
            return "identity"
        elif any(t in q_lower for t in symbolic_triggers):
            return "symbolic"
        return "conceptual"

    @staticmethod
    def _extract_entities_from_query(query):
        patterns = [
            (r"\bGalaxy X-\d+\b", "galaxy"), 
            (r"\bProject [A-Z][a-z]+\b", "project"), 
            (r"\bID[:\s]\d+\b", "id"),
            (r"\b[A-Z]{2,}-\d+\b", "code")
        ]
        entities = []
        for p, t in patterns:
            found = re.findall(p, query, re.IGNORECASE)
            for f in found:
                entities.append({"type": t, "id": f.strip()})
        return entities

    @staticmethod
    def _extract_relations_from_query(query):
        q_lower = query.lower()
        relations = []
        if "primary" in q_lower or "main" in q_lower or "cause" in q_lower:
            relations.append("primary_emission")
        if "secondary" in q_lower or "signature" in q_lower:
            relations.append("secondary_signature")
        if "tertiary" in q_lower or "trace" in q_lower:
            relations.append("tertiary_trace")
        return relations

    def _generate_candidates(self, user_id, query, agent_id, limit=1000):
        """Stage 1: Broad Recall (Nuclear Depth)"""
        # Pool A: Lexical/FTS5
        episodic_candidates = self.episodic.search(user_id, query, agent_id=agent_id, limit=limit)
        
        # Pool B: Semantic ANN
        semantic_results = self.semantic.search(user_id, query, top_k=limit)
        
        candidates = []
        seen_ids = set()
        
        # Merge by Memory ID
        for c in episodic_candidates:
            cid = c.get("id")
            if cid and cid not in seen_ids:
                c["pool"] = "A"
                c["semantic_score"] = 0.5
                candidates.append(c)
                seen_ids.add(cid)
                
        for s in semantic_results:
            if s.get("agent_id") == agent_id or s.get("memory_type") == "shared":
                sqlite_id = s.get("sqlite_id")
                if sqlite_id and sqlite_id not in seen_ids:
                    real_m = self.episodic.get_by_id(user_id, sqlite_id)
                    if real_m:
                        real_m["pool"] = "B"
                        real_m["semantic_score"] = s.get("score", 0.5)
                        candidates.append(real_m)
                        seen_ids.add(sqlite_id)
        
        return candidates

    def _rank_candidates(self, query, candidates, query_type):
        """Stage 2: Precision-Biased Ranking"""
        context = {
            "query_entities": self._extract_entities_from_query(query),
            "query_relations": self._extract_relations_from_query(query),
            "recall_engine": self 
        }
        
        # Fine-tuned weights for Resilient Cognitive Retrieval
        weights = {
            "symbolic": {"semantic": 0.01, "lexical": 0.04, "entity": 0.45, "relation": 0.45, "salience": 0.0, "temporal": 0.05},
            "identity": {"semantic": 0.05, "lexical": 0.10, "entity": 0.70, "relation": 0.10, "salience": 0.0, "temporal": 0.05},
            "conceptual": {"semantic": 0.60, "lexical": 0.10, "entity": 0.10, "relation": 0.10, "salience": 0.05, "temporal": 0.05}
        }.get(query_type, {"semantic": 0.5, "lexical": 0.1, "entity": 0.1, "relation": 0.1, "salience": 0.1, "temporal": 0.1})

        for c in candidates:
            signals = {}
            for name, scorer in self.scorers.items():
                signals.update(scorer.score(query, c, context))
            
            # Dynamic Tiered Weighting: 
            # 1. Fresh Data (< 1 hour): Recency is King (Timeline Sort)
            # 2. Old Data (> 1 hour): Importance is King (Knowledge Sort)
            age_sec = time.time() - float(c.get("timestamp", 0.0))
            current_weights = weights.copy()
            
            if age_sec < 3600: # Fresh
                current_weights["temporal"] = 0.40 # High recency boost for timeline
                current_weights["salience"] = 0.05
            else: # Old
                current_weights["temporal"] = 0.05
                current_weights["salience"] = 0.40 # High importance boost for long-term knowledge
            
            # Weighted Fusion
            final_score = 0.0
            for sig, weight in current_weights.items():
                final_score += signals.get(sig, 0.5) * weight
            
            # Explainability breakdown
            c["unified_score"] = final_score
            c["explain"] = {k: v for k, v in signals.items() if k in weights}
            
            # Confidence Floor: Squelch hallucinations
            if c["unified_score"] < 0.2:
                c["unified_score"] *= 0.1 # Exponential drop for low-confidence matches
                c["is_uncertain"] = True

            # Resilient Multiplier: Soft suppression instead of hard vaporizing
            if signals.get("exact_match") == False and context["query_entities"]:
                c["unified_score"] *= 0.3 # Allow semantic rescue for extraction failures
                c["rejected_reason"] = "entity_mismatch"
        
        candidates.sort(key=lambda x: x["unified_score"], reverse=True)
        return candidates

    def multi_stage_recall(self, user_id, query, agent_id="default_agent", top_k=5):
        t0 = time.time()
        
        # 1. Candidate Generation
        candidates = self._generate_candidates(user_id, query, agent_id)
        candidate_count = len(candidates)
        
        # 2. Primary Ranking
        query_type = self._classify_query(query)
        ranked = self._rank_candidates(query, candidates, query_type)
        
        # 3. Truth Arbitration (Epistemic Discipline)
        from .truth_engine import TruthEngine
        truth_engine = TruthEngine(threshold=0.35)
        
        # Build context for Truth Engine
        query_context = {
            "query_entities": self._extract_entities_from_query(query),
            "query_relations": self._extract_relations_from_query(query)
        }
        resolved, status = truth_engine.resolve(ranked, query_context)
        
        # 4. Adaptive Recovery: If Truth Engine squelches symbolic but we have semantic candidates
        if status == "UNCERTAIN" and query_type in ["symbolic", "identity"]:
            print(f"[RecallEngine] Truth Engine rejected symbolic matches. Triggering Semantic Recovery...")
            ranked_conceptual = self._rank_candidates(query, candidates, "conceptual")
            resolved, status = truth_engine.resolve(ranked_conceptual, query_context)
        
        # 5. Finalization
        final_memories = resolved[:top_k]
        self._reinforce_memories(user_id, final_memories)
        
        return {
            "intent": query_type,
            "status": status,
            "memories": final_memories,
            "metrics": {
                "total_candidates": candidate_count,
                "latency_ms": round((time.time() - t0) * 1000, 1),
                "truth_status": status
            },
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
                m_id = m.get("id")
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
        except: pass
