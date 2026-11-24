from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    documents = relationship("Document", back_populates="kb", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    kb_id = Column(Integer, ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000))
    file_size = Column(Integer, default=0)
    status = Column(String(20), default="uploading")  # uploading/parsing/indexing/ready/failed
    error_reason = Column(Text)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    kb = relationship("KnowledgeBase", back_populates="documents")


class AgentKBBinding(Base):
    __tablename__ = "agent_kb_bindings"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    kb_id = Column(Integer, ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False)
    top_k = Column(Integer, default=3)
    similarity_threshold = Column(Float, default=0.7)
    
    agent = relationship("Agent", back_populates="kb_bindings")
    kb = relationship("KnowledgeBase")
