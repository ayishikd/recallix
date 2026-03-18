import math
import time

class DecayLogic:
    @staticmethod
    def calculate_strength(base_importance, last_accessed, access_count):
        """
        Human-like memory strength based on Ebbinghaus Forgetting Curve.
        R = e^(-t/S) where R is retention, t is time, S is stability.
        """
        # Time elapsed in hours (for development we might use seconds)
        # Using seconds for demonstration purposes
        # Default to current time if never accessed
        if last_accessed is None:
            last_accessed = time.time()
            
        t = time.time() - last_accessed
        
        # Stability S increases with more accesses
        stability = (base_importance * 0.5) * (1 + math.log(access_count + 1))
        
        # Prevent division by zero
        stability = max(stability, 0.1)
        
        # R = e^(-t/S)
        retention = math.exp(-t / (stability * 3600)) # Scale stability to hours
        
        # For dev/demo: scale to seconds instead of hours if elapsed time is short
        if t < 3600:
             retention = math.exp(-t / stability)
             
        return retention * base_importance

    @staticmethod
    def reinforce(access_count):
        return access_count + 1
