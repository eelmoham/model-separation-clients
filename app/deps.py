from fastapi import Header, HTTPException
from app.config import API_KEYS

def get_current_client(x_api_key: str = Header(...)):
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return API_KEYS[x_api_key]
