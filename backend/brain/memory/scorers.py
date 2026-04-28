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
        
        norm_bm25 = min(bm25 / 10.0, 1.0)
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
                    
                    # Normalized comparison (handles hyphens/casing)
                    m_id_clean = re.sub(r"[^a-z0-9]+", "", m_id)
                    q_id_clean = re.sub(r"[^a-z0-9]+", "", q_id)
                    
                    if m_id_clean == q_id_clean:
                        exact_match = True
                        break
                    elif m_type == q_type and m_id != q_id:
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
            
        rel_match = 0.5
        if query_relations and m_relations:
            # Binary lock for relation intent
            if any(q_rel in m_relations for q_rel in query_relations):
                rel_match = 1.0
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
        recency = math.exp(-age / 86400.0) 
        return {"temporal": round(recency, 3)}
