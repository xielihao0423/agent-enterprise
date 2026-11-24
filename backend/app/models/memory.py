from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class MemoryConfig(Base):
    __tablename__ = "memory_configs"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    agent_scope_enabled = Column(Boolean, default=False)
    user_scope_enabled = Column(Boolean, default=False)
    session_scope_enabled = Column(Boolean, default=False)
    write_strategy = Column(String(20), default="auto")  # auto/manual
    
    agent = relationship("Agent", back_populates="memory_config")


class MemoryEntry(Base):
    __tablename__ = "memory_entries"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    scope = Column(String(20), nullable=False)  # agent/user/session
    user_id = Column(String(100))
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
