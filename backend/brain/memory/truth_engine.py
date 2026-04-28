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

        # 1. Sort by Score + Recency (Tie-breaker for evolving truths)
        # We sort primarily by unified_score (desc) and secondarily by timestamp (desc)
        ranked_memories.sort(key=lambda x: (x.get("unified_score", 0.0), x.get("timestamp", 0.0)), reverse=True)

        # 2. Hard Abstention Gate (Squelch Hallucinations)
        top_score = ranked_memories[0].get("unified_score", 0.0)
        if top_score < self.threshold:
            print(f"[TruthEngine] Abstaining: Top score {top_score:.2f} below threshold {self.threshold:.2f}")
            return [], "UNCERTAIN"

        # 2. Temporal Slot Arbitration
        # We group by (Entity, Relation) and only keep the latest valid fact.
        resolved_memories = []
        seen_slots = set()

        for mem in ranked_memories:
            # Extract symbolic slot (Entity + Relation)
            # Handle cases where metadata might still be a JSON string from SQLite
            metadata = mem.get("metadata", {})
            if isinstance(metadata, str):
                try:
                    import json
                    metadata = json.loads(metadata)
                except:
                    metadata = {}

            entities = metadata.get("entities", [])
            relations = metadata.get("relations", [])
            
            # Create a unique key for the truth slot
            # e.g., ("Galaxy X-55", "primary_emission")
            slot_key = None
            if entities and relations:
                ent_id = entities[0].get("id") if isinstance(entities[0], dict) else entities[0]
                rel_type = relations[0].get("type") if isinstance(relations[0], dict) else relations[0]
                slot_key = (str(ent_id).lower(), str(rel_type).lower())

            if slot_key:
                if slot_key not in seen_slots:
                    mem["truth_status"] = "verified"
                    resolved_memories.append(mem)
                    seen_slots.add(slot_key)
                else:
                    mem["truth_status"] = "superseded"
                    # We don't discard entirely, but we lower their priority
            else:
                # Conceptual/General memory with no clear symbolic slot
                resolved_memories.append(mem)

        return resolved_memories, "CONSISTENT"
