from dotenv import load_dotenv
load_dotenv()
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.public.public_api import router as public_router
from backend.api.internal.internal_api import router as internal_router
from backend.api.agents.router import router as agents_router
from backend.api.deps import get_memory_manager

app = FastAPI(title="Recallix API")

# Fix #14: Environment-configurable CORS
allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(public_router)
app.include_router(internal_router)
app.include_router(agents_router)

# Initialize global memory manager
memory = get_memory_manager()

@app.get("/")
async def root():
    return {"message": "Recallix API is running (Audit Mode)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
