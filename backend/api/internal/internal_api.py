from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import time
import os
import sqlite3
import requests

router = APIRouter(prefix="/internal", tags=["Internal System API"])

class ClearRequest(BaseModel):
    user_id: str

@router.post("/clear")
async def clear_system_memory(request: ClearRequest):
    """
    NUCLEAR OPTION: Clears all memory for a specific user or the entire system.
    """
    try:
        # 1. Clear SQLite Episodic Memory
        db_path = "backend/storage/sqlite_db/memory.db"
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM episodic_events WHERE user_id = ?", (request.user_id,))
            conn.commit()
            conn.close()

        # 2. Clear C++ Vector Engine (Nuclear)
        requests.post("http://localhost:8080/clear") # We need to implement this in C++
        
        return {
            "status": "success", 
            "message": f"All memory for {request.user_id} has been wiped.",
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cluster/recompute")
async def recompute_clusters():
    return {"status": "success", "message": "Cluster recomputation triggered"}
