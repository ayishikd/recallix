# API Reference

The MemoryOS API allows you to interact with the cognitive memory architecture.

## Authentication
All requests must include the `X-API-Key` header.

## Public Endpoints

### POST `/memory/store`
Stores a new memory event.
**Body:**
```json
{
  "content": "string",
  "metadata": "object (optional)"
}
```

### POST `/memory/recall`
Retrieves relevant memories for a query.
**Body:**
```json
{
  "query": "string",
  "limit": "int (optional, default: 10)"
}
```

### GET `/memory/timeline`
Retrieves the chronological event timeline.

### GET `/memory/insights`
Retrieves the AI's high-level reflections and insights.

---

## Internal Endpoints (Maintenance)

### POST `/internal/cluster/recompute`
Triggers memory clustering recomputation.

### POST `/internal/vector/reindex`
Triggers vector index rebuilding.

### POST `/internal/meta/analyze`
Manually triggers the meta-memory analysis loop.
