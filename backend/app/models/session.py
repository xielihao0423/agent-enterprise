from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(100))
    source = Column(String(20), default="web")  # feishu/web
    chat_type = Column(String(20), default="single")  # single/group
    chat_id = Column(String(200))  # feishu chat_id for mapping
    status = Column(String(20), default="idle")  # idle/running/interrupted/closed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    agent = relationship("Agent", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # user/assistant/tool
    content = Column(Text)
    attachments = Column(JSON)  # JSON array of attachment info
    token_usage = Column(Integer, default=0)
    tool_calls = Column(JSON)  # JSON array of tool call traces
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    session = relationship("Session", back_populates="messages")
