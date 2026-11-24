from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.db.session import Base


class FeishuBot(Base):
    __tablename__ = "feishu_bots"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    app_id = Column(String(200), nullable=False)
    app_secret_encrypted = Column(String(500), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="SET NULL"))
    connection_mode = Column(String(20), default="long_polling")  # webhook/long_polling
    status = Column(String(20), default="disconnected")  # connected/disconnected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
