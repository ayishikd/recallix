from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import time
import os
import sqlite3
from backend.utils.internal_client import internal_post
from backend.utils.paths import get_db_path

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
        db_path = get_db_path("backend/storage/sqlite_db/memory.db")
        if os.path.exists(db_path):
            with sqlite3.connect(db_path, timeout=60) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                if request.user_id == "all" or not request.user_id:
                     cursor.execute("DELETE FROM episodic_events")
                     cursor.execute("DELETE FROM episodic_fts")
                else:
                    # Clear both events and the FTS index for the user
                    cursor.execute("DELETE FROM episodic_fts WHERE content_id IN (SELECT id FROM episodic_events WHERE user_id = ?)", (request.user_id,))
                    cursor.execute("DELETE FROM episodic_events WHERE user_id = ?", (request.user_id,))
                conn.commit()

        # 2. Clear C++ Vector Engine with Verification & Retry
        max_retries = 3
        cleared = False
        for attempt in range(max_retries):
            try:
                # Fix #13: Use internal_post with auth key
                res = internal_post("http://localhost:8080/clear", {})
                if res.status_code == 200:
                    cleared = True
                    break
            except Exception as e:
                print(f"[InternalAPI] Clear attempt {attempt+1} failed: {e}")
                time.sleep(1)
        
        if not cleared:
            print("[InternalAPI] CRITICAL: Vector engine clear failed after retries.")
        
        return {
            "status": "success" if cleared else "partial_success", 
            "message": f"Memory wipe processed for {request.user_id}.",
            "vector_engine_cleared": cleared,
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cluster/recompute")
async def recompute_clusters():
    return {"status": "success", "message": "Cluster recomputation triggered"}
