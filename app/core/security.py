from fastapi import Header, HTTPException

from app.config import settings

API_KEY = settings.api_key

def verify_api_key(x_api_key: str = Header()):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")