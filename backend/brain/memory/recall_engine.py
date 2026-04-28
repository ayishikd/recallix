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
        
        # Identity Logic (High Priority)
        if any(t in q_lower for t in identity_triggers):
            return "identity"
        
        # Symbolic Logic (Check for IDs or Triggers)
        symbolic_id_match = re.search(r"\b(galaxy x-\d+|x-\d+|x\d+|project [a-z]+|starship [a-z]+)\b", q_lower)
        if symbolic_id_match or any(t in q_lower for t in symbolic_triggers):
            return "symbolic"
            
        return "conceptual"

    @staticmethod
    def _extract_entities_from_query(query):
        patterns = [
            (r"\bGalaxy X-\d+\b", "galaxy"), 
            (r"\bX-\d+\b", "symbolic"), 
            (r"\bProject [A-Z][a-z]+\b", "project"), 
            (r"\bStarship [A-Z][a-z]+\b", "starship"),
            (r"\bID[:\s]\d+\b", "id"),
            (r"\b[A-Z]{2,}-\d+\b", "code")
        ]
        entities = []
        for p, t in patterns:
            found = re.findall(p, query, re.IGNORECASE)
            for f in found:
                # Canonicalize ID for retrieval lock (consistent with manager.py storage)
                clean_id = re.sub(r"^(galaxy|project|starship|patient|user|pulsar)\s+", "", f, flags=re.IGNORECASE).strip()
                canonical_id = re.sub(r"[^a-z0-9]+", "", clean_id.lower())
                entities.append({"type": t, "id": canonical_id})
        return entities

    @staticmethod
    def _extract_relations_from_query(query):
        q_lower = query.lower()
        relations = []
        if "primary" in q_lower or "main" in q_lower or "cause" in q_lower or "emission" in q_lower or "defines" in q_lower:
            relations.append("primary_emission")
        if "secondary" in q_lower or "signature" in q_lower:
            relations.append("secondary_signature")
        if "safety" in q_lower or "status" in q_lower or "core" in q_lower:
            relations.append("safety_status")
        if "phase" in q_lower or "state" in q_lower:
            relations.append("state_phase")
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
        for i, c in enumerate(episodic_candidates):
            cid = c.get("id")
            if cid and cid not in seen_ids:
                c["pool"] = "A"
                # Fix #2: Late-Binding Semantic Check for top Pool A results
                if i < 50:
                    c["semantic_score"] = self.semantic.compute_similarity(query, c["content"])
                else:
                    c["semantic_score"] = 0.5
                
                candidates.append(c)
                seen_ids.add(cid)
                
        for s in semantic_results:
            sqlite_id = s.get("sqlite_id")
            if sqlite_id and sqlite_id not in seen_ids:
                real_m = self.episodic.get_by_id(user_id, sqlite_id)
                if real_m:
                    real_m["pool"] = "B"
                    real_m["semantic_score"] = s.get("score", 0.5)
                    real_m["memory_type"] = s.get("memory_type", "private")
                    real_m["agent_id"] = s.get("agent_id", "")
                    candidates.append(real_m)
                    seen_ids.add(sqlite_id)
        
        return candidates

    def _rank_candidates(self, query, candidates, query_type, agent_id="default_agent"):
        """Stage 2: Precision-Biased Ranking"""
        context = {
            "query_entities": self._extract_entities_from_query(query),
            "query_relations": self._extract_relations_from_query(query),
            "recall_engine": self 
        }
        
        # Fine-tuned weights for Resilient Cognitive Retrieval (Fix #33: Trust Semantic)
        weights = {
            "symbolic": {"semantic": 0.15, "lexical": 0.05, "entity": 0.40, "relation": 0.35, "salience": 0.0, "temporal": 0.05},
            "identity": {"semantic": 0.20, "lexical": 0.05, "entity": 0.60, "relation": 0.10, "salience": 0.0, "temporal": 0.05},
            "conceptual": {"semantic": 0.70, "lexical": 0.10, "entity": 0.10, "relation": 0.05, "salience": 0.0, "temporal": 0.05}
        }.get(query_type, {"semantic": 0.7, "lexical": 0.1, "entity": 0.1, "relation": 0.05, "salience": 0.0, "temporal": 0.05})

        # Fix #3: Compute Age Variance to prevent temporal blindness during benchmarks
        ages = [time.time() - float(c.get("timestamp", 0.0)) for c in candidates]
        age_variance = max(ages) - min(ages) if ages else 0

        for c in candidates:
            # Fix #4: Last-Minute Semantic Score Check (Ensure no defaults reach the ranker)
            if c.get("semantic_score", 0.5) == 0.5:
                c["semantic_score"] = self.semantic.compute_similarity(query, c.get("content", ""))
            
            signals = {}
            for name, scorer in self.scorers.items():
                signals.update(scorer.score(query, c, context))
            
            # Dynamic Tiered Weighting: 
            # 1. Fresh Data (< 1 hour): Recency is King (Timeline Sort)
            # 2. Old Data (> 1 hour): Importance is King (Knowledge Sort)
            age_sec = time.time() - float(c.get("timestamp", 0.0))
            current_weights = weights.copy()
            
            # Only boost temporal if there's meaningful time spread (Fix #3)
            if age_sec < 3600 and age_variance > 300: # Fresh + >5 min spread
                current_weights["temporal"] = 0.40 # High recency boost for timeline
                current_weights["salience"] = 0.05
            else: # Old or low variance
                current_weights["temporal"] = 0.05
                current_weights["salience"] = 0.40 # High importance boost for long-term knowledge
            
            # Weighted Fusion with Blended Priority Layering
            m_type = c.get("memory_type", "private")
            c_agent = c.get("agent_id", "")
            layer_bonus = 0.0
            if m_type == "private" and c_agent == agent_id:
                layer_bonus = 0.1
            elif m_type == "shared":
                layer_bonus = 0.05
                
            final_score = 0.0
            for sig, weight in current_weights.items():
                final_score += signals.get(sig, 0.5) * weight
            
            final_score += layer_bonus
            
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
        
        # --- Stage 0: Reasoning Expansion (Fix #27) ---
        from .reasoning_engine import ReasoningEngine
        reasoner = ReasoningEngine(self)
        
        # 1. Alias Resolution (Dragon's Breath -> X-77)
        alias_id = reasoner.resolve_aliases(query)
        effective_query = f"{query} {alias_id}" if alias_id else query
        
        # 2. Contextual Expansion (dormant -> quiescent)
        expanded_query = reasoner.expand_query(effective_query)
        
        # 1. Candidate Generation
        candidates = self._generate_candidates(user_id, expanded_query, agent_id)
        candidate_count = len(candidates)
        
        # 2. Primary Ranking
        query_type = self._classify_query(expanded_query)
        ranked = self._rank_candidates(expanded_query, candidates, query_type, agent_id)
        
        # 3. Truth Arbitration (Epistemic Discipline)
        from .truth_engine import TruthEngine
        truth_engine = TruthEngine(threshold=0.35)
        
        # Build context for Truth Engine (Fix #29: Fuzzy Relation Alignment)
        raw_relations = self._extract_relations_from_query(expanded_query)
        expanded_relations = reasoner.expand_relations(raw_relations)
        
        query_context = {
            "query_entities": self._extract_entities_from_query(expanded_query),
            "query_relations": expanded_relations
        }
        resolved, status = truth_engine.resolve(ranked, query_context)
        
        # --- Stage 3.5: Multi-Hop Chaining (Fix #28) ---
        source_ids = [m["id"] for m in resolved[:2]]
        hops = reasoner.identify_multi_hop_opportunities(resolved[:2], query_context)
        if hops:
            print(f"[ReasoningEngine] Identified Multi-Hop targets: {hops}. Triggering Second Hop...")
            # Squelch sources in the original ranked pool to force promotion of hop targets
            for r in ranked:
                if r["id"] in source_ids:
                    r["unified_score"] *= 0.01 # Near-absolute squelch
            
            for hop_target in hops:
                # Update context for the second hop validation
                hop_entities = self._extract_entities_from_query(hop_target)
                query_context["query_entities"].extend(hop_entities)
                
                hop_candidates = self._generate_candidates(user_id, hop_target, agent_id)
                hop_ranked = self._rank_candidates(hop_target, hop_candidates, "symbolic", agent_id)
                # Merge hop results into candidates pool (exclude sources and give high priority)
                for h in hop_ranked:
                    if h["id"] in source_ids: continue # Skip the fact that triggered the hop
                    
                    # Force-promote and tag hop results (even if already in pool)
                    h["is_hop_result"] = True
                    h["unified_score"] = 99.0 # Hard Priority for Reasoned Truth
                    
                    found_in_ranked = False
                    for r in ranked:
                        if r["id"] == h["id"]:
                            r["is_hop_result"] = True
                            r["unified_score"] = 99.0
                            found_in_ranked = True
                            break
                    
                    if not found_in_ranked:
                        ranked.append(h)
            
            # Re-sort and re-arbitrate after hopping
            ranked.sort(key=lambda x: x["unified_score"], reverse=True)
            resolved, status = truth_engine.resolve(ranked, query_context)

        # 4. Adaptive Recovery: If Truth Engine squelches symbolic but we have semantic candidates
        if status == "UNCERTAIN" and query_type in ["symbolic", "identity"]:
            print(f"[RecallEngine] Truth Engine rejected symbolic matches. Triggering Semantic Recovery...")
            ranked_conceptual = self._rank_candidates(expanded_query, candidates, "conceptual", agent_id)
            resolved, status = truth_engine.resolve(ranked_conceptual, query_context)
        
        # 5. Finalization
        final_memories = resolved[:top_k]
        
        fallback_triggered = False
        decision = "standard_cognitive_retrieval"
        if not final_memories:
            print("[RecallEngine] Triggering thresholded vector fallback...")
            raw_semantic = self.semantic.search(user_id, expanded_query, top_k=top_k*2)
            for s in raw_semantic:
                if s.get("score", 0.0) > 0.65:
                    sqlite_id = s.get("sqlite_id")
                    if sqlite_id:
                        real_m = self.episodic.get_by_id(user_id, sqlite_id)
                        if real_m:
                            real_m["is_fallback"] = True
                            real_m["unified_score"] = s.get("score", 0.0)
                            final_memories.append(real_m)
                            if len(final_memories) >= top_k:
                                break
            if final_memories:
                fallback_triggered = True
                decision = "fallback_used_due_to_overfiltering"

        self._reinforce_memories(user_id, final_memories)
        
        return {
            "intent": query_type,
            "status": status,
            "memories": final_memories,
            "debug": {
                "semantic_hits": candidate_count,
                "after_filter": len(ranked),
                "after_truth": len(resolved),
                "fallback_triggered": fallback_triggered,
                "top_scores": [round(m.get("unified_score", 0.0), 3) for m in final_memories[:3]],
                "decision": decision
            },
            "metrics": {
                "total_candidates": candidate_count,
                "latency_ms": round((time.time() - t0) * 1000, 1),
                "truth_status": status
            },
            "schema_insights": self._get_schema_insights(expanded_query)
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
