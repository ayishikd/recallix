import time
import os
import sqlite3
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.api.middleware.auth import verify_api_key
from backend.api.deps import get_memory_manager
from backend.brain.world_model.state_inference import StateInference
from backend.brain.meta_memory.meta_memory_engine import MetaMemoryEngine

router = APIRouter(prefix="/memory", tags=["Public Memory API"])
memory_manager = get_memory_manager()
state_inference = StateInference()
meta_engine = MetaMemoryEngine()

class StoreRequest(BaseModel):
    content: str
    user_id: Optional[str] = None
    agent_id: Optional[str] = "default_agent"
    memory_type: Optional[str] = "private"
    metadata: Optional[dict] = None
    skip_llm: Optional[bool] = False
    sync_index: Optional[bool] = False

class RecallRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    agent_id: Optional[str] = "default_agent"
    limit: Optional[int] = 10

@router.post("/store")
async def store_memory(request: StoreRequest, auth=Depends(verify_api_key)):
    user_id = request.user_id or auth["user_id"]
    result = memory_manager.store(
        user_id, 
        request.content, 
        agent_id=request.agent_id,
        memory_type=request.memory_type,
        skip_llm=request.skip_llm,
        sync_index=request.sync_index
    )
    return {
        "status": "success",
        "data": {
            "message": "Memory stored successfully",
            "importance": result.get("importance"),
            "schemas": result.get("schemas", []),
            "promoted": result.get("promoted", False),
            "total_ms": result.get("total_ms"),
            "processing_log": result.get("processing_log", [])
        },
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }

@router.post("/recall")
async def recall_memory(request: RecallRequest, auth=Depends(verify_api_key)):
    user_id = request.user_id or auth["user_id"]
    results = memory_manager.retrieve(user_id, request.query, agent_id=request.agent_id, limit=request.limit)
    
    return {
        "status": "success",
        "data": {
            "memories": results.get("memories", []),
            "intent": results.get("intent", "unknown"),
            "confidence": results.get("confidence", 0.0),
            "retrieval_plan": results.get("retrieval_plan", {}),
            "context_inference": results.get("context_inference", {}),
            "schema_insights": results.get("schema_insights", []),
            "latency_ms": results.get("latency_ms", 0.0),
            "debug": results.get("debug", {})
        },
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }

@router.delete("/{memory_id}")
async def delete_memory(memory_id: int, auth=Depends(verify_api_key)):
    user_id = auth["user_id"]
    memory_manager.delete(user_id, memory_id)
    return {
        "status": "success",
        "data": {"message": f"Memory {memory_id} deleted"},
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }

@router.get("/timeline")
async def get_timeline(auth=Depends(verify_api_key)):
    user_id = auth["user_id"]
    events = memory_manager.timeline.get_sequence(user_id)
    return {
        "status": "success",
        "data": events,
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }

@router.get("/insights")
async def get_insights(auth=Depends(verify_api_key)):
    user_id = auth["user_id"]
    reflections = memory_manager.reflective.get_reflections(user_id)
    return {
        "status": "success",
        "data": reflections,
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }

@router.get("/world-state")
async def get_world_state(auth=Depends(verify_api_key)):
    user_id = auth["user_id"]
    states = state_inference.get_states(user_id)
    return {
        "status": "success",
        "data": states,
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }

@router.get("/meta-insights")
async def get_meta_insights(auth=Depends(verify_api_key)):
    insights = meta_engine.get_latest_insights(limit=20)
    return {
        "status": "success",
        "data": insights,
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }

@router.get("/stats")
async def get_stats(auth=Depends(verify_api_key)):
    user_id = auth["user_id"]
    
    # Count episodic memories
    episodic_count = 0
    db_path = "backend/storage/sqlite_db/memory.db"
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path, timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM episodic_events")
            episodic_count = cursor.fetchone()[0]
            conn.close()
        except: pass

    # Count timeline events
    timeline_count = 0
    tl_path = "backend/storage/timeline_store/timeline.db"
    if os.path.exists(tl_path):
        try:
            conn = sqlite3.connect(tl_path, timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM events")
            timeline_count = cursor.fetchone()[0]
            conn.close()
        except: pass

    # Count reflections
    reflection_count = 0
    ref_path = "backend/storage/sqlite_db/reflections.db"
    if os.path.exists(ref_path):
        try:
            conn = sqlite3.connect(ref_path, timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM reflections")
            reflection_count = cursor.fetchone()[0]
            conn.close()
        except: pass

    # Count evolved schemas
    evolved_schema_count = 0
    schema_db_path = "backend/storage/schema_registry/schemas.db"
    if os.path.exists(schema_db_path):
        try:
            conn = sqlite3.connect(schema_db_path, timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM evolved_schemas")
            evolved_schema_count = cursor.fetchone()[0]
            conn.close()
        except: pass

    # Count agents
    agent_count = 0
    agent_db_path = "backend/storage/agent_registry.db"
    if os.path.exists(agent_db_path):
        try:
            conn = sqlite3.connect(agent_db_path, timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM agents")
            agent_count = cursor.fetchone()[0]
            conn.close()
        except: pass

    return {
        "status": "success",
        "data": {
            "episodic_memories": episodic_count,
            "timeline_events": timeline_count,
            "reflections": reflection_count,
            "evolved_schemas": evolved_schema_count,
            "active_agents": agent_count,
            "user_id": user_id
        },
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }

@router.get("/profile")
async def get_profile(auth=Depends(verify_api_key)):
    user_id = auth["user_id"]
    states = state_inference.get_states(user_id)
    reflections = memory_manager.reflective.get_reflections(user_id, limit=3)
    return {
        "status": "success",
        "data": {
            "user_id": user_id,
            "world_states": states,
            "top_reflections": reflections
        },
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }
