import time
from .intent_detector import IntentDetector
from .context_inference import ContextInference
from .retrieval_planner import RetrievalPlanner
from .memory_router import MemoryRouter
from .context_builder import ContextBuilder

class IntentRetrievalManager:
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager
        self.intent_detector = IntentDetector()
        self.context_inference = ContextInference(memory_manager)
        self.planner = RetrievalPlanner()
        self.router = MemoryRouter(memory_manager)
        self.builder = ContextBuilder(token_limit=2000)

    def execute_intent_recall(self, user_id, query, agent_id="default_agent"):
        start_time = time.time()
        
        # 1. Intent Detection (Cached internally in detector)
        intent_data = self.intent_detector.detect(query)
            
        # 2. Task Context Inference
        context = self.context_inference.infer(query, intent_data, agent_id)
        
        # 3. Retrieval Planner
        plan = self.planner.generate_plan(context, query, agent_id=agent_id)
        
        # 4. Memory Router (Execution)
        raw_results = self.router.route_retrieval(plan, user_id, agent_id)
        
        # 5. Context Builder (Final Set)
        final_memories = self.builder.build(raw_results, plan["memory_filters"])
        
        total_latency = (time.time() - start_time) * 1000
        
        return {
            "intent": intent_data["intent"],
            "confidence": intent_data["confidence"],
            "retrieval_plan": plan,
            "context_inference": context,
            "memories": final_memories,
            "latency_ms": total_latency
        }
