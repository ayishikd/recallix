from fastapi import Request, HTTPException
import json
import os

AUTH_FILE = "backend/storage/api_keys.json"

async def verify_api_key(request: Request):
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(status_code=401, detail="API Key missing")
    
    if not os.path.exists(AUTH_FILE):
        raise HTTPException(status_code=500, detail="Auth configuration missing")
        
    with open(AUTH_FILE, 'r') as f:
        auth_data = json.load(f)
        
    if api_key not in auth_data.get("keys", {}):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    return auth_data["keys"][api_key]
