from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class AuditLogResponse(BaseModel):
    id: int
    operator: Optional[str] = None
    action: str
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    detail: Optional[Any] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TokenUsageResponse(BaseModel):
    agent_id: int
    agent_name: str
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_calls: int = 0


class ErrorStatResponse(BaseModel):
    error_type: str
    count: int
    latest_at: Optional[datetime] = None
