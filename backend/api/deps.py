from backend.brain.memory.manager import MemoryManager

# Singleton instance to prevent multiple model loads (Fix #3)
_memory_manager = None

def get_memory_manager():
    global _memory_manager
    if _memory_manager is None:
        print("[DEPS] Initializing global MemoryManager singleton...")
        _memory_manager = MemoryManager()
    return _memory_manager
