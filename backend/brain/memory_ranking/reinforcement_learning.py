class MemoryRL:
    def __init__(self, learning_rate=0.1, decay_factor=0.95):
        self.learning_rate = learning_rate
        self.decay_factor = decay_factor

    def calculate_value(self, importance, reinforcement_score):
        """
        memory_value = importance_score * reinforcement_score
        """
        # importance is 0.0-1.0 (internal 1-10)
        # reinforcement_score starts at 1.0
        return (importance / 10.0) * reinforcement_score

    def reinforce_positive(self, current_score):
        """
        reinforcement_score = reinforcement_score + learning_rate
        """
        return current_score + self.learning_rate

    def reinforce_negative(self, current_score):
        """
        reinforcement_score = reinforcement_score * decay_factor
        """
        return current_score * self.decay_factor

    def get_policy(self, value, importance, age_days):
        """
        Determines the action for a memory based on its value, importance, and age.
        """
        # Protect high importance
        if importance >= 8.0:
            return "protect"
        
        # Keep high value (well-reinforced)
        if value > 0.6:
            return "keep"
            
        # Archive medium-low value / old
        if importance <= 5.0 and age_days > 30:
            return "archive"
            
        # Delete very low value / old
        if importance <= 3.0 and age_days > 7:
            return "delete"
            
        return "keep"
