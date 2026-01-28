from sqlalchemy import Column, String
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from app.db import Base


class Message(Base):
    __tablename__ = "messages"

    message_id = Column(String, primary_key=True)
    from_msisdn = Column(String, nullable=False)
    to_msisdn = Column(String, nullable=False)
    ts = Column(String, nullable=False)        # ISO-8601 UTC string
    text = Column(String, nullable=True)

    created_at = Column(
        String,
        nullable=False,
        server_default=func.strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
    )
