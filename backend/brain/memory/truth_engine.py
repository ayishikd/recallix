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
        import json
        from collections import defaultdict
        
        now = time.time()
        tau = 86400 * 7 # 1 week
        
        groups = defaultdict(list)
        
        for mem in ranked_memories:
            # Unified Clamped Scoring before grouping
            semantic_score = mem.get("unified_score", 0.0)
            timestamp = float(mem.get("timestamp", 0.0))
            access_count = float(mem.get("retrieval_count", 0))
            
            recency_score = max(0.2, math.exp(-(now - timestamp) / tau))
            access_freq_norm = min(1.0, access_count / 10.0)
            
            if not mem.get("is_hop_result") and not mem.get("is_fallback"):
                mem["unified_score"] = (semantic_score * 0.6) + (recency_score * 0.3) + (access_freq_norm * 0.1)

            # Slot Assignment
            metadata = mem.get("metadata", {})
            if isinstance(metadata, str):
                try: metadata = json.loads(metadata)
                except: metadata = {}

            slots = metadata.get("slots", [])
            slot_id = None
            if slots and isinstance(slots, list):
                slot_id = slots[0].get("slot_id")
                mem["_slot_value"] = slots[0].get("value")
            
            if slot_id:
                mem["_slot_id"] = slot_id
                groups[slot_id].append(mem)
            else:
                groups["unstructured"].append(mem)

        resolved_memories = []
        
        # 4. Resolve Each Slot
        for slot_id, items in groups.items():
            if slot_id == "unstructured":
                for m in items:
                    m["truth_status"] = "verified"
                    resolved_memories.append(m)
                continue
            
            # Sort chronologically to walk history
            items = sorted(items, key=lambda x: float(x.get("timestamp", 0.0)))
            
            active = None
            for m in items:
                content = str(m.get("content", "")).lower()
                # Explicit Negation
                if " not " in content or content.startswith("not "):
                    active = None
                    m["truth_status"] = "invalid"
                    continue
                
                # Explicit Override Detection
                if active and m.get("_slot_value") != active.get("_slot_value"):
                    active["truth_status"] = "superseded"
                    active["superseded_by"] = m.get("id")
                
                m["truth_status"] = "active"
                active = m
            
            if active:
                active["truth_status"] = "verified"
                resolved_memories.append(active)
        
        # Enforce Final Return Contract: At most ONE value per slot_id
        for slot_id, items in groups.items():
            if slot_id != "unstructured":
                # Ensure only one is marked verified in the resolved_memories
                verified_in_slot = [m for m in resolved_memories if m.get("_slot_id") == slot_id and m.get("truth_status") == "verified"]
                assert len(verified_in_slot) <= 1, f"Bug in Truth Engine: Multiple verified truths for {slot_id}"

        # 5. Re-sort by updated unified_score
        resolved_memories.sort(key=lambda x: (
            x.get("is_hop_result", False),
            x.get("unified_score", 0.0)
        ), reverse=True)

        return resolved_memories, "CONSISTENT"
