from fastapi import APIRouter, Response, status
from app.config import settings
from app.db import engine
from sqlalchemy import text

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/live")
def liveness():
    """Always return 200 once the app is running[cite: 122]."""
    return {"status": "alive"}

@router.get("/ready")
def readiness():
    """Return 200 only if DB is reachable and WEBHOOK_SECRET is set ."""
    try:
        # 1. Check DB connectivity [cite: 126]
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # 2. Check if WEBHOOK_SECRET is configured [cite: 127]
        if not settings.webhook_secret:
            return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        return {"status": "ready"}
    except Exception:
        # Return 503 if any check fails [cite: 128]
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)