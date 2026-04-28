import math

class MemoryRL:
    def __init__(self, learning_rate=0.1, decay_factor=0.95):
        self.learning_rate = learning_rate
        self.decay_factor = decay_factor
        self.MAX_REINFORCEMENT = 10.0

    def calculate_value(self, importance, reinforcement_score):
        """
        memory_value = importance_score * reinforcement_score
        """
        # importance is 1-10
        # reinforcement_score is 1-10
        # Normalize to 0-1
        return (importance / 10.0) * (reinforcement_score / 10.0)

    def reinforce_positive(self, current_score):
        """
        Fix #12: Sigmoid-style saturation to prevent unbounded growth.
        As score increases, the effective learning rate decreases.
        """
        if current_score >= self.MAX_REINFORCEMENT:
            return self.MAX_REINFORCEMENT
            
        # Logistic-ish growth: slower as we approach ceiling
        growth = self.learning_rate * (1.0 - (current_score / self.MAX_REINFORCEMENT))
        return min(current_score + growth, self.MAX_REINFORCEMENT)

    def reinforce_negative(self, current_score):
        """
        reinforcement_score = reinforcement_score * decay_factor
        """
        return max(current_score * self.decay_factor, 1.0)

    def get_policy(self, value, importance, age_days):
        """
        Determines the action for a memory based on its value, importance, and age.
        """
        # Protect high importance
        if importance >= 8.0:
            return "protect"
        
        # Keep high value (well-reinforced)
        # Value is now normalized 0-1
        if value > 0.6:
            return "keep"
            
        # Archive medium-low value / old
        if importance <= 5.0 and age_days > 30:
            return "archive"
            
        # Delete very low value / old
        if importance <= 3.0 and age_days > 7:
            return "delete"
            
        return "keep"
