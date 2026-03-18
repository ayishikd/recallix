from fastapi import FastAPI, Body
from pydantic import BaseModel
from ..memory.manager import MemoryManager
from ..utils.background_worker import BackgroundWorker

app = FastAPI()
memory = MemoryManager()
worker = BackgroundWorker(memory)

@app.on_event("startup")
async def startup_event():
    worker.start()

class Event(BaseModel):
    user_id: str
    message: str

@app.post("/memory/store")
async def store_memory(event: Event):
    memory.store(event.user_id, event.message)
    return {"status": "success"}

@app.get("/memory/retrieve")
async def retrieve_memory(user_id: str, query: str):
    return memory.retrieve(user_id, query)

@app.post("/memory/reflect")
async def reflect_memory(user_id: str = "user_123"):
    # In a real system, LLM would generate reflection
    # Mock reflection for now
    memory.reflective.store_reflection(user_id, "User shows strong interest in system architecture and memory layers.", [1, 2], 0.85)
    return {"status": "reflected"}

@app.get("/memory/graph_query")
async def graph_query(user_id: str, id: str):
    # This would call C++ infra
    return {"neighbors": []}

@app.post("/memory/promote")
async def promote_memory(user_id: str, event_id: int):
    # Logic to manually promote an episodic event to long-term
    # This would involve looking up the event and calling LT promote
    return {"status": "not_implemented"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
