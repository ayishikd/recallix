import time
import threading
from ..schema_engine.detector import PatternDetector
from ..schema_engine.proposer import SchemaGenerator
from ..schema_engine.migration.engine import MigrationEngine
from ..schema_engine.registry.manager import SchemaRegistry

class EvolutionWorker:
    def __init__(self, memory_manager, interval=3600):
        self.manager = memory_manager
        self.interval = interval
        self.running = False
        self.detector = PatternDetector()
        self.registry = SchemaRegistry()
        self.proposer = SchemaGenerator(self.registry)
        self.migration = MigrationEngine(memory_manager.episodic)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print("[EvolutionWorker] Started.")

    def _run(self):
        while self.running:
            try:
                self.evolve()
            except Exception as e:
                print(f"[EvolutionWorker] Error during evolution: {e}")
            time.sleep(self.interval)

    def evolve(self):
        print("[EvolutionWorker] Starting evolution cycle...")
        # 1. Fetch recent episodic memories (e.g., last 1000)
        # Using list_all for bulk access
        memories = self.manager.episodic.list_all(limit=1000)
        
        # 2. Detect Patterns
        patterns = self.detector.detect_patterns(memories)
        
        # 3. Process Patterns
        for p in patterns:
            # Check if this pattern is already structured
            # (Simple check: is the pattern word already a schema name?)
            existing = [s for s in self.registry.list_schemas() if p["pattern"].lower() in s["name"].lower()]
            if existing:
                continue
                
            print(f"[EvolutionWorker] Detected new pattern: '{p['pattern']}' ({p['count']} occurrences)")
            
            # 4. Propose and Register Schema
            proposal = self.proposer.propose_schema(p)
            
            # 5. Migrate Memories
            count = self.migration.migrate_to_schema(p["memories"], proposal)
            print(f"[EvolutionWorker] Evolved schema '{proposal['name']}' and migrated {count} memories.")

        print("[EvolutionWorker] Cycle complete.")
