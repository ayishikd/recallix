import time

class TruthEngine:
    """
    Recallix Truth Engine v1: The Epistemic Discipline Layer.
    Responsible for temporal arbitration, hard abstention, and conflict resolution.
    """
    def __init__(self, threshold=0.35):
        self.threshold = threshold

    def resolve(self, ranked_memories, query_context):
        """
        Arbitrate between competing memories and enforce truth consistency.
        """
        if not ranked_memories:
            return [], "NO_MATCH"

        # 1. Sort by Hop Priority + Score + Recency
        # We prioritize facts discovered via Reasoning Engine (is_hop_result)
        ranked_memories.sort(key=lambda x: (
            x.get("is_hop_result", False),
            x.get("unified_score", 0.0), 
            x.get("timestamp", 0.0)
        ), reverse=True)

        # 2. Hard Abstention Gate (Squelch Hallucinations)
        top_mem = ranked_memories[0]
        top_score = top_mem.get("unified_score", 0.0)
        is_reasoned = top_mem.get("is_hop_result", False)
        
        if top_score < self.threshold and not is_reasoned:
            print(f"[TruthEngine] Abstaining: Top score {top_score:.2f} below threshold {self.threshold:.2f}")
            return [], "UNCERTAIN"

        # 3. Temporal Slot Arbitration (State Transitions)
        import math
        now = time.time()
        tau = 86400 * 7 # 1 week
        
        slot_groups = {}
        for mem in ranked_memories:
            metadata = mem.get("metadata", {})
            if isinstance(metadata, str):
                try: metadata = json.loads(metadata)
                except: metadata = {}

            entities = metadata.get("entities", [])
            relations = metadata.get("relations", [])
            
            slot_key = None
            if entities and relations:
                ent_id = entities[0].get("id") if isinstance(entities[0], dict) else entities[0]
                rel_type = relations[0].get("type") if isinstance(relations[0], dict) else relations[0]
                slot_key = (str(ent_id).lower(), str(rel_type).lower())
            
            if slot_key:
                slot_groups.setdefault(slot_key, []).append(mem)

        # Implicit Overrides: The newest memory for a slot is the truth
        slot_truths = {}
        for slot_key, group in slot_groups.items():
            slot_truths[slot_key] = max(group, key=lambda x: float(x.get("timestamp", 0.0)))

        resolved_memories = []
        for mem in ranked_memories:
            # Unified Clamped Scoring
            semantic_score = mem.get("unified_score", 0.0)
            timestamp = float(mem.get("timestamp", 0.0))
            access_count = float(mem.get("retrieval_count", 0))
            
            recency_score = max(0.2, math.exp(-(now - timestamp) / tau))
            access_freq_norm = min(1.0, access_count / 10.0)
            
            if not mem.get("is_hop_result") and not mem.get("is_fallback"):
                mem["unified_score"] = (semantic_score * 0.6) + (recency_score * 0.3) + (access_freq_norm * 0.1)

            # Slot check
            metadata = mem.get("metadata", {})
            if isinstance(metadata, str):
                try: metadata = json.loads(metadata)
                except: metadata = {}
            entities = metadata.get("entities", [])
            relations = metadata.get("relations", [])
            
            slot_key = None
            if entities and relations:
                ent_id = entities[0].get("id") if isinstance(entities[0], dict) else entities[0]
                rel_type = relations[0].get("type") if isinstance(relations[0], dict) else relations[0]
                slot_key = (str(ent_id).lower(), str(rel_type).lower())

            if slot_key:
                if slot_truths[slot_key] == mem:
                    mem["truth_status"] = "verified"
                    resolved_memories.append(mem)
                else:
                    mem["truth_status"] = "superseded"
            else:
                resolved_memories.append(mem)

        # Re-sort by updated unified_score
        resolved_memories.sort(key=lambda x: (
            x.get("is_hop_result", False),
            x.get("unified_score", 0.0)
        ), reverse=True)

        return resolved_memories, "CONSISTENT"
