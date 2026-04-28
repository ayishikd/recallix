import re
import math
import time
import json

class SignalScorer:
    """Base class for modular signal scorers."""
    def score(self, query, memory, context):
        raise NotImplementedError

class SemanticScorer(SignalScorer):
    def score(self, query, memory, context):
        score = memory.get("semantic_score", 0.5)
        return {"semantic": round(score, 3)}

class LexicalScorer(SignalScorer):
    def score(self, query, memory, context):
        bm25 = memory.get("bm25_score", 0.0)
        if bm25 == 0.0:
            content = memory.get("content", "").lower()
            q_words = set(query.lower().split())
            c_words = set(content.split())
            overlap = len(q_words.intersection(c_words)) / max(len(q_words), 1)
            bm25 = overlap * 5.0
        
        # SQLite FTS5 returns negative BM25 (lower is better). 
        # We need magnitude (higher is better) for the unified ranker.
        mag_bm25 = abs(bm25)
        norm_bm25 = min(mag_bm25 / 20.0, 1.0)
        return {"lexical": round(norm_bm25, 3)}

class EntityScorer(SignalScorer):
    def score(self, query, memory, context):
        query_entities = context.get("query_entities", [])
        metadata = memory.get("metadata", {})
        if isinstance(metadata, str):
            try: metadata = json.loads(metadata)
            except: metadata = {}
            
        m_entities = metadata.get("entities", [])
        content = memory.get("content", "").lower()
        
        # Fallback extraction if missing
        if not m_entities:
            from .recall_engine import RecallEngine
            m_entities = RecallEngine._extract_entities_from_query(content)

        exact_match = False
        collision = False
        
        if m_entities and query_entities:
            for q_ent in query_entities:
                q_id = str(q_ent.get("id")).lower()
                q_type = q_ent.get("type")
                
                for m_ent in m_entities:
                    m_id = str(m_ent.get("id") if isinstance(m_ent, dict) else m_ent).lower()
                    m_type = m_ent.get("type") if isinstance(m_ent, dict) else "general"
                    
                    # Normalized comparison (Canonical Mapping: strip prefixes, non-alphanumerics)
                    def canonicalize(s):
                        clean = re.sub(r"^(galaxy|project|starship|patient|user|pulsar)\s+", "", s, flags=re.IGNORECASE).strip()
                        return re.sub(r"[^a-z0-9]+", "", clean.lower())
                    
                    m_id_clean = canonicalize(m_id)
                    q_id_clean = canonicalize(q_id)
                    
                    if m_id_clean == q_id_clean:
                        exact_match = True
                        break
                    elif m_type == q_type and m_id_clean != q_id_clean:
                        collision = True
            
        # Absolute Lock Signal for Identity alignment
        score = 0.5
        if exact_match: score = 1.0
        elif collision: score = 0.0
        
        return {"entity": score, "exact_match": exact_match}

class RelationScorer(SignalScorer):
    def score(self, query, memory, context):
        query_relations = context.get("query_relations", [])
        metadata = memory.get("metadata", {})
        if isinstance(metadata, str):
            try: metadata = json.loads(metadata)
            except: metadata = {}
        
        m_relations = metadata.get("relations", [])
        if not m_relations:
            from .recall_engine import RecallEngine
            content = memory.get("content", "").lower()
            m_relations = RecallEngine._extract_relations_from_query(content)
        
        # Normalize m_relations to a set of strings for fast, robust comparison
        norm_m_rels = set()
        for r in m_relations:
            if isinstance(r, dict):
                norm_m_rels.add(r.get("type", "").lower())
            else:
                norm_m_rels.add(str(r).lower())
            
        rel_match = 0.5
        content = memory.get("content", "").lower()
        
        # Emergency Check: If no symbolic relations, check for literal phrase match
        if not norm_m_rels and query_relations:
            for q_rel in query_relations:
                clean_q_rel = q_rel.replace("_", " ")
                if clean_q_rel in content:
                    norm_m_rels.add(q_rel.lower())
        
        if query_relations and norm_m_rels:
            # 1. Structural Identity Lock
            if any(q_rel.lower() in norm_m_rels for q_rel in query_relations):
                rel_match = 0.8 # Base match for correct relation type
                
                # 2. Logical Probing: Check for primary/secondary/tertiary distinction in content
                if "primary" in query.lower() or "primary_emission" in query_relations:
                    if "primary" in content or "main" in content or "dominant" in content:
                        rel_match = 1.0
                    elif "secondary" in content or "tertiary" in content:
                        rel_match = 0.2 # Active mismatch penalty
                elif "secondary" in query.lower() or "secondary_signature" in query_relations:
                    if "secondary" in content or "signature" in content:
                        rel_match = 1.0
                    elif "primary" in content:
                        rel_match = 0.2
            else:
                rel_match = 0.0
        
        return {"relation": rel_match}

class SalienceScorer(SignalScorer):
    def score(self, query, memory, context):
        importance = float(memory.get("importance", 5.0)) / 10.0
        reinforcement = float(memory.get("reinforcement_score", 1.0)) / 10.0
        salience = (importance * 0.7) + (reinforcement * 0.3)
        return {"salience": round(salience, 3)}

class TemporalScorer(SignalScorer):
    def score(self, query, memory, context):
        ts = float(memory.get("timestamp", time.time()))
        age = max(0, time.time() - ts)
        
        # High-Resolution Tiers for Cognitive Focus
        if age < 60: # Last minute (Active Session)
            recency = 1.0
        elif age < 3600: # Last hour (Recent Memory)
            recency = 0.8
        elif age < 86400: # Last day (Fresh Knowledge)
            recency = 0.5
        else: # Historical
            recency = 0.1
            
        return {"temporal": round(recency, 3)}
