from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class SessionCreate(BaseModel):
    user_id: Optional[str] = "web_user"
    source: str = "web"
    chat_type: str = "single"


class SessionResponse(BaseModel):
    id: int
    agent_id: int
    user_id: Optional[str] = None
    source: str
    chat_type: str
    chat_id: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    message_count: int = 0
    
    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str
    attachments: Optional[List[Any]] = None


class MessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: Optional[str] = None
    attachments: Optional[Any] = None
    token_usage: int = 0
    tool_calls: Optional[Any] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SessionStatusUpdate(BaseModel):
    status: str  # closed
