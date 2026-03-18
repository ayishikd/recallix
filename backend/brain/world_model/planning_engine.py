from ..models.model_router import ModelRouter

class PlanningEngine:
    def __init__(self, memory_manager):
        self.memory = memory_manager
        self.router = ModelRouter()

    def generate_plan(self, user_id, prediction, current_state):
        """
        Creates a helpful plan based on current state and predicted needs.
        """
        prompt = (
            f"Prediction: {prediction}\n"
            f"User State: {current_state}\n\n"
            f"Generate a multi-step cognitive plan to assist the user proactively. "
            f"The plan should be stored as actionable insights."
        )
        
        plan = self.router.route("reasoning", prompt)
        
        # Store plan in knowledge graph context (mocking for now)
        # self.memory.graph.add_node(f"plan_{user_id}", "plan")
        
        return plan
