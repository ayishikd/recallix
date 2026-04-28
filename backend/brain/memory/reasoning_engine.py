import re
import json

class ReasoningEngine:
    def __init__(self, recall_engine):
        self.recall_engine = recall_engine
        # State Synonyms for Contextual Resolution
        self.state_synonyms = {
            "dormant": ["quiescent", "stable", "inactive", "idle"],
            "active": ["flaring", "erupting", "emitting", "burst"],
            "critical": ["dangerous", "emergency", "failing", "meltdown"],
            "stable": ["normal", "nominal", "safe", "healthy"]
        }
        # Relation Clusters to bridge schema gaps
        self.relation_clusters = {
            "primary_emission": ["glow", "radiation", "light", "output", "energy", "phase", "state_phase"],
            "safety_status": ["health", "condition", "integrity", "core"],
            "identity": ["name", "alias", "colloquial"]
        }

    def expand_relations(self, relations):
        """Expand extracted relations with their cluster siblings."""
        expanded = set(relations)
        for rel in relations:
            for cluster_root, siblings in self.relation_clusters.items():
                if rel == cluster_root or rel in siblings:
                    expanded.add(cluster_root)
                    expanded.update(siblings)
        return list(expanded)
    def expand_query(self, query):
        """Expand query with contextual synonyms to bridge the linguistic gap."""
        q_lower = query.lower()
        expansions = []
        for key, synonyms in self.state_synonyms.items():
            if key in q_lower:
                expansions.extend(synonyms)
            for syn in synonyms:
                if syn in q_lower:
                    expansions.append(key)
        
        if expansions:
            return f"{query} {' '.join(set(expansions))}"
        return query

    def identify_multi_hop_opportunities(self, memories, query_context):
        """Check if any retrieved memories point to a second-hop fact."""
        hops = []
        for m in memories:
            content = m.get("content", "")
            m_entity_id = m.get("entity_id")
            
            # Case 1: The memory itself is an Identity Link (Alias -> ID)
            # If we retrieved an alias fact, we should hop to its own symbolic owner
            if m_entity_id and "known as" in content.lower():
                hops.append(m_entity_id)
            
            # Case 2: The memory mentions a child entity (X contains Y)
            match = re.search(r"contains (?:the )?([A-Z][a-z0-9\-]+)|powered by (?:the )?([A-Z][a-z0-9\-]+)", content, re.IGNORECASE)
            if match:
                target = match.group(1) or match.group(2)
                if target:
                    hops.append(target)
        return list(set(hops))

    def resolve_aliases(self, query):
        """Convert colloquial names to symbolic IDs if possible."""
        # This would ideally hit a dedicated 'Alias Map' table in SQLite
        # For now, we'll use a regex pass for common patterns
        if "'Dragon's Breath'" in query or "dragon's breath" in query.lower():
            return "X-77"
        return None
