from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    avatar = Column(String(500))
    status = Column(String(20), default="draft")  # draft/active/inactive/deleted
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    role_files = relationship("RoleFile", back_populates="agent", cascade="all, delete-orphan")
    model_binding = relationship("AgentModelBinding", back_populates="agent", uselist=False, cascade="all, delete-orphan")
    skill_bindings = relationship("AgentSkillBinding", back_populates="agent", cascade="all, delete-orphan")
    kb_bindings = relationship("AgentKBBinding", back_populates="agent", cascade="all, delete-orphan")
    memory_config = relationship("MemoryConfig", back_populates="agent", uselist=False, cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="agent", cascade="all, delete-orphan")


class RoleFile(Base):
    __tablename__ = "role_files"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    file_type = Column(String(20), nullable=False)  # agent_md/user_md/identity_md/soul_md
    content = Column(Text, default="")
    version = Column(Integer, default=1)
    is_current = Column(Boolean, default=True)
    operator = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    agent = relationship("Agent", back_populates="role_files")
