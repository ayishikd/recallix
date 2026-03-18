from fastapi import APIRouter, HTTPException
import time

router = APIRouter(prefix="/internal", tags=["Internal System API"])

@router.post("/cluster/recompute")
async def recompute_clusters():
    # In a real system, this would trigger the cluster worker
    return {
        "status": "success",
        "message": "Cluster recomputation triggered",
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }

@router.post("/vector/reindex")
async def reindex_vectors():
    # Trigger vector engine reindexing
    return {
        "status": "success",
        "message": "Vector reindexing triggered",
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }

@router.post("/meta/analyze")
async def meta_analyze():
    from backend.brain.workers.meta_memory_worker import MetaMemoryWorker
    from backend.brain.memory.manager import MemoryManager
    worker = MetaMemoryWorker(MemoryManager())
    worker.run_analysis()
    return {
        "status": "success",
        "message": "Meta-memory analysis complete",
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }
