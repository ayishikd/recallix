import time
import json

class SchemaGenerator:
    def __init__(self, registry):
        self.registry = registry

    def propose_schema(self, pattern_details):
        """
        Takes a pattern (e.g., from PatternDetector) and generates a schema proposal.
        """
        pattern_name = pattern_details["pattern"]
        schema_id = f"evolved_{pattern_name}_{int(time.time())}"
        
        # Heuristic for fields: 
        # For a simple local version, we'll start with standard fields and 
        # maybe extract specific entities later.
        fields = ["topic", "context", "occurrence_count", "last_updated"]
        
        proposal = {
            "schema_id": schema_id,
            "name": f"{pattern_name.capitalize()} Context",
            "fields": fields,
            "confidence": 0.85  # Default confidence for detected patterns
        }
        
        # Register in the SchemaRegistry
        self.registry.register_schema(
            proposal["schema_id"], 
            proposal["name"], 
            proposal["fields"], 
            proposal["confidence"]
        )
        
        return proposal
