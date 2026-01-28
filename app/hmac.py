import hmac
import hashlib
from fastapi import Request, HTTPException, Header
from app.config import settings

async def verify_signature(request: Request, x_signature: str = Header(None)):
    if not x_signature:
        raise HTTPException(status_code=401, detail="invalid signature")
    
    body = await request.body()
    expected_sig = hmac.new(
        settings.webhook_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(expected_sig, x_signature):
        raise HTTPException(status_code=401, detail="invalid signature")