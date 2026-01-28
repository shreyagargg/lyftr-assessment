from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import re

class WebhookPayload(BaseModel):
    message_id: str = Field(..., min_length=1)
    from_msisdn: str = Field(..., alias="from") 
    to_msisdn: str = Field(..., alias="to")
    ts: str  # Must be ISO-8601 UTC with Z
    text: Optional[str] = Field(None, max_length=4096)

    @field_validator("from_msisdn", "to_msisdn")
    @classmethod
    def validate_msisdn(cls, v: str):
        if not re.match(r"^\+\d+$", v):
            raise ValueError("Must be E.164 format (+ then digits)")
        return v
    
    class Config:
        populate_by_name = True

# --- ADD THESE FOR THE /messages ENDPOINT ---

class MessageSchema(BaseModel):
    message_id: str
    from_msisdn: str = Field(..., alias="from")
    to_msisdn: str = Field(..., alias="to")
    ts: str
    text: Optional[str]

    class Config:
        from_attributes = True  # Allows Pydantic to read SQLAlchemy objects
        populate_by_name = True

class MessageListResponse(BaseModel):
    data: List[MessageSchema]
    total: int
    limit: int
    offset: int

# --- ADD THIS FOR THE /stats ENDPOINT (Next Step) ---

class StatsResponse(BaseModel):
    total_messages: int
    unique_senders: int
    unique_recipients: int

    