import logging
import hmac
import hashlib
from fastapi import FastAPI, Depends, HTTPException, Request, Header
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy import asc, func

from app.config import settings
from app.logging_config import setup_logging
from app.health import router as health_router
from app.db import Base, engine, get_db
from app.models import Message

# Import your schemas from schemas.py
from app.schemas import WebhookPayload, MessageListResponse, StatsResponse

# 1. Setup Structured JSON Logging
setup_logging()
logger = logging.getLogger(__name__)

# 2. Global counters for Metrics
REQUEST_COUNT = 0
ERROR_COUNT = 0

# 3. Initialize Database Tables
Base.metadata.create_all(bind=engine)

# 4. Define the FastAPI App
app = FastAPI(title=settings.app_name)

# 5. Middleware for Observability (Metrics)
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    global REQUEST_COUNT, ERROR_COUNT
    REQUEST_COUNT += 1
    try:
        response = await call_next(request)
        if response.status_code >= 400:
            ERROR_COUNT += 1
        return response
    except Exception as e:
        ERROR_COUNT += 1
        raise e

# 6. Include Health Router
app.include_router(health_router)

# 7. HMAC Signature Verification Logic
async def verify_signature(request: Request, x_signature: str = Header(None)):
    if not x_signature:
        logger.error("Missing X-Signature", extra={"result": "invalid_signature"})
        raise HTTPException(status_code=401, detail="invalid signature")
    
    body = await request.body()
    
    # Crucial: This allows the body to be read again by the Pydantic WebhookPayload
    async def receive():
        return {"type": "http.request", "body": body}
    request._receive = receive 
    
    expected_sig = hmac.new(
        settings.webhook_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(expected_sig, x_signature):
        logger.error("Invalid Signature", extra={"result": "invalid_signature"})
        raise HTTPException(status_code=401, detail="invalid signature")

# --- ROUTES ---

@app.get("/")
def root():
    return {"app": settings.app_name, "env": settings.env}

@app.post("/webhook")
async def webhook(
    payload: WebhookPayload, 
    db: Session = Depends(get_db),
    _ = Depends(verify_signature)
):
    """Ingest messages exactly once (Idempotency)."""
    existing = db.query(Message).filter(Message.message_id == payload.message_id).first()
    if existing:
        logger.info("Duplicate message", extra={
            "message_id": payload.message_id, 
            "dup": True, 
            "result": "duplicate"
        })
        return {"status": "ok"}

    try:
        new_msg = Message(
            message_id=payload.message_id,
            from_msisdn=payload.from_msisdn,
            to_msisdn=payload.to_msisdn,
            ts=payload.ts,
            text=payload.text
        )
        db.add(new_msg)
        db.commit()
        logger.info("Message created", extra={
            "message_id": payload.message_id, 
            "dup": False, 
            "result": "created"
        })
        return {"status": "ok"}
    except Exception as e:
        db.rollback()
        logger.error(f"Persistence error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/messages", response_model=MessageListResponse)
def get_messages(
    limit: int = 50, 
    offset: int = 0, 
    from_msisdn: str | None = None, 
    since: str | None = None, 
    q: str | None = None, 
    db: Session = Depends(get_db)
):
    """Paginated and filterable message list."""
    limit = max(1, min(100, limit))
    offset = max(0, offset)
    query = db.query(Message)

    if from_msisdn:
        query = query.filter(Message.from_msisdn == from_msisdn)
    if since:
        query = query.filter(Message.ts >= since)
    if q:
        query = query.filter(Message.text.ilike(f"%{q}%"))

    total = query.count()
    # Deterministic ordering
    messages = query.order_by(asc(Message.ts), asc(Message.message_id)).limit(limit).offset(offset).all()

    return {
        "data": messages,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@app.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """Simple analytical statistics."""
    total_msgs = db.query(Message).count()
    unique_senders = db.query(func.count(func.distinct(Message.from_msisdn))).scalar()
    unique_recipients = db.query(func.count(func.distinct(Message.to_msisdn))).scalar()
    
    return {
        "total_messages": total_msgs,
        "unique_senders": unique_senders,
        "unique_recipients": unique_recipients
    }

@app.get("/metrics")
def get_metrics():
    """Prometheus-style metrics endpoint."""
    lines = [
        "# HELP http_requests_total Total number of HTTP requests.",
        "# TYPE http_requests_total counter",
        f"http_requests_total {REQUEST_COUNT}",
        "# HELP http_errors_total Total number of HTTP errors (4xx/5xx).",
        "# TYPE http_errors_total counter",
        f"http_errors_total {ERROR_COUNT}"
    ]
    return PlainTextResponse("\n".join(lines))