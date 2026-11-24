from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class ModelProvider(Base):
    __tablename__ = "model_providers"
    id = Column(Integer, primary_key=True, index=True)
    provider_type = Column(String(20), nullable=False)  # ark/openai
    name = Column(String(100), nullable=False)
    api_key_encrypted = Column(String(500), nullable=False)
    base_url = Column(String(500))
    available_models = Column(Text)  # JSON array of model names
    status = Column(String(20), default="available")  # available/unavailable
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AgentModelBinding(Base):
    __tablename__ = "agent_model_bindings"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    provider_id = Column(Integer, ForeignKey("model_providers.id"), nullable=False)
    model_name = Column(String(100), nullable=False)
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=4096)
    top_p = Column(Float, default=0.9)
    
    agent = relationship("Agent", back_populates="model_binding")
    provider = relationship("ModelProvider")
