import sqlite3
import json

class MigrationEngine:
    def __init__(self, episodic_memory):
        self.episodic = episodic_memory

    def migrate_to_schema(self, memories, schema_proposal):
        """
        Migrates a set of raw memories into a structured schema format.
        For now, we update the schema_tags in episodic_events.
        """
        schema_id = schema_proposal["schema_id"]
        schema_name = schema_proposal["name"]
        
        # In a real system, we might promote these to a 'structured_memories' table.
        # Here, we'll append the new schema_id to the existing tags.
        for m in memories:
            m_id = m["id"]
            current_tags = m.get("schema_tags", "[]")
            if isinstance(current_tags, str):
                try:
                    tags_list = json.loads(current_tags) if current_tags.startswith('[') else [current_tags]
                except:
                    tags_list = [current_tags]
            else:
                tags_list = current_tags or []
            
            if schema_id not in tags_list:
                tags_list.append(schema_id)
            
            # Persist back to DB
            self._update_tags(m_id, tags_list)
        
        return len(memories)

    def _update_tags(self, memory_id, tags_list):
        conn = sqlite3.connect(self.episodic.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE episodic_events 
            SET schema_tags = ?
            WHERE id = ?
        ''', (json.dumps(tags_list), memory_id))
        conn.commit()
        conn.close()
