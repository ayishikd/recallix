import json
import os

class PolicyOptimizer:
    def __init__(self, policy_path="backend/storage/memory_policies.json"):
        self.policy_path = policy_path
        self._init_policy()

    def _init_policy(self):
        if not os.path.exists(self.policy_path):
            default_policies = {
                "importance_weights": {
                    "user_goals": 1.2,
                    "recency": 1.0,
                    "reinforcement": 1.1
                },
                "forgetting_thresholds": {
                    "archive_days": 30,
                    "delete_days": 7
                }
            }
            os.makedirs(os.path.dirname(self.policy_path), exist_ok=True)
            with open(self.policy_path, 'w') as f:
                json.dump(default_policies, f, indent=2)

    def optimize_policies(self, metrics):
        """
        Adjusts weights and thresholds based on performance metrics.
        """
        # metrics could include recall failure rates, etc.
        # For now, we simulate adjustment
        with open(self.policy_path, 'r') as f:
            policies = json.load(f)

        adjustments = []
        # Example: If recall is low, increase importance weights
        if metrics.get("low_recall_rate", 0) > 0.2:
            policies["importance_weights"]["user_goals"] += 0.1
            adjustments.append("Increased importance weight for user_goals due to low recall.")

        # Save if changed
        if adjustments:
            with open(self.policy_path, 'w') as f:
                json.dump(policies, f, indent=2)
        
        return adjustments
