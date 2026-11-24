from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.db.session import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    operator = Column(String(100))
    action = Column(String(100), nullable=False)
    target_type = Column(String(50))
    target_id = Column(String(100))
    detail = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
