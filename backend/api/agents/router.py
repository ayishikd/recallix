from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.brain.memory.manager import MemoryManager
from typing import List, Optional
from backend.api.middleware.auth import verify_api_key
from backend.api.deps import get_memory_manager
import time

router = APIRouter(prefix="/agents", tags=["Multi-Agent Memory API"])

class AgentStoreRequest(BaseModel):
    content: str
    agent_id: str
    memory_type: Optional[str] = "private" # "private" or "shared"
    metadata: Optional[dict] = None

class AgentRecallRequest(BaseModel):
    query: str
    agent_id: str
    limit: Optional[int] = 10

@router.post("/store")
async def store_agent_memory(request: AgentStoreRequest, auth=Depends(verify_api_key), memory_manager: MemoryManager = Depends(get_memory_manager)):
    """
    Dedicated endpoint for agents to store memories with specific agent context.
    """
    user_id = auth["user_id"]
    result = memory_manager.store(
        user_id, 
        request.content, 
        agent_id=request.agent_id, 
        memory_type=request.memory_type
    )
    return {
        "status": "success",
        "data": {
            "message": f"Memory stored for agent {request.agent_id}",
            "agent_id": request.agent_id,
            "memory_type": request.memory_type,
            "importance": result.get("importance"),
            "total_ms": result.get("total_ms")
        },
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }

@router.post("/recall")
async def recall_agent_memory(request: AgentRecallRequest, auth=Depends(verify_api_key), memory_manager: MemoryManager = Depends(get_memory_manager)):
    """
    Dedicated endpoint for agents to retrieve memories (private + shared).
    """
    user_id = auth["user_id"]
    results = memory_manager.retrieve(user_id, request.query, agent_id=request.agent_id)
    return {
        "status": "success",
        "data": results,
        "agent_id": request.agent_id,
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }

@router.get("/list")
async def list_registered_agents(auth=Depends(verify_api_key)):
    from backend.agents.registry.manager import AgentRegistry
    registry = AgentRegistry()
    agents = registry.list_agents()
    return {
        "status": "success",
        "data": agents,
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }

@router.get("/schemas")
async def list_evolved_schemas(auth=Depends(verify_api_key)):
    from backend.brain.schema_engine.registry.manager import SchemaRegistry
    registry = SchemaRegistry()
    schemas = registry.list_schemas()
    return {
        "status": "success",
        "data": schemas,
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }
