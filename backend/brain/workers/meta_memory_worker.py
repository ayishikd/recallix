import time
from ..meta_memory.meta_memory_engine import MetaMemoryEngine
from ..meta_memory.meta_analyzer import MetaAnalyzer
from ..meta_memory.schema_optimizer import SchemaOptimizer
from ..meta_memory.policy_optimizer import PolicyOptimizer

class MetaMemoryWorker:
    def __init__(self, memory_manager):
        self.memory = memory_manager
        self.engine = MetaMemoryEngine()
        self.analyzer = MetaAnalyzer()
        self.schema_opt = SchemaOptimizer()
        self.policy_opt = PolicyOptimizer()

    def run_analysis(self, user_id="user_123"):
        print(f"[MetaMemoryWorker] Starting analysis for {user_id}...")
        
        # 1. Detect patterns
        patterns = self.analyzer.detect_patterns(user_id)
        if not patterns:
            print("[MetaMemoryWorker] No significant patterns detected.")
            return

        # 2. Optimize schemas
        schema_insights = self.schema_opt.optimize_schemas(patterns)
        for insight in schema_insights:
            self.engine.store_insight("schema_evolution", insight, 0.85, "knowledge_graph")
            print(f"[MetaMemoryWorker] Schema insight: {insight}")

        # 3. Optimize policies (simple mock metrics for now)
        # In a real system, these would come from self-testing or recall logs
        mock_metrics = {"low_recall_rate": 0.25} 
        policy_insights = self.policy_opt.optimize_policies(mock_metrics)
        for insight in policy_insights:
            self.engine.store_insight("policy_adjustment", insight, 0.75, "attention_controller")
            print(f"[MetaMemoryWorker] Policy insight: {insight}")

        print("[MetaMemoryWorker] Analysis complete.")
