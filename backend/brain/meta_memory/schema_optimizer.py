import json
import os

class SchemaOptimizer:
    def __init__(self, registry_path="backend/storage/schema_registry.json"):
        self.registry_path = registry_path

    def optimize_schemas(self, patterns):
        """
        Updates the schema registry based on detected patterns.
        """
        if not os.path.exists(self.registry_path):
            return []

        with open(self.registry_path, 'r') as f:
            registry = json.load(f)

        new_insights = []
        existing_schemas = [s["name"] for s in registry.get("schemas", [])]

        for pattern in patterns:
            theme = pattern["theme"]
            schema_name = f"{theme}_interest"
            
            if schema_name not in existing_schemas:
                # Evolve schema
                new_schema = {
                    "name": schema_name,
                    "description": f"Automated schema for recurring interest in {theme}",
                    "tags": [theme],
                    "created_by": "meta_memory"
                }
                registry["schemas"].append(new_schema)
                new_insights.append(f"Created new schema: {schema_name}")

        if new_insights:
            with open(self.registry_path, 'w') as f:
                json.dump(registry, f, indent=2)

        return new_insights
