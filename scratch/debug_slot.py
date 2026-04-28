import sys
from backend.brain.memory.manager import MemoryManager

mm = MemoryManager()
res1 = mm.store("test_user", "The secret project code is OMEGA-VOID", skip_llm=True)
print("STORE 1:", res1)
res2 = mm.store("test_user", "The secret project code is SolarFlameOcean", skip_llm=True)
print("STORE 2:", res2)

recall = mm.retrieve("test_user", "What is the secret project code?")
print("RECALL:", recall)
