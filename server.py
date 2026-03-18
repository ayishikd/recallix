from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.public.public_api import router as public_router
from backend.api.internal.internal_api import router as internal_router
from backend.api.agents.router import router as agents_router
from backend.brain.memory.manager import MemoryManager
from backend.brain.utils.background_worker import BackgroundWorker

app = FastAPI(title="Memoize API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(public_router)
app.include_router(internal_router)
app.include_router(agents_router)

memory = MemoryManager()
worker = BackgroundWorker(memory)

@app.on_event("startup")
async def startup_event():
    worker.start()

@app.get("/")
async def root():
    return {"message": "MemoryOS API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
