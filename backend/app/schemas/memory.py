from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MemoryConfigUpdate(BaseModel):
    agent_scope_enabled: Optional[bool] = None
    user_scope_enabled: Optional[bool] = None
    session_scope_enabled: Optional[bool] = None
    write_strategy: Optional[str] = None  # auto/manual


class MemoryConfigResponse(BaseModel):
    agent_scope_enabled: bool
    user_scope_enabled: bool
    session_scope_enabled: bool
    write_strategy: str
    
    class Config:
        from_attributes = True


class MemoryEntryCreate(BaseModel):
    scope: str  # agent/user/session
    user_id: Optional[str] = None
    session_id: Optional[int] = None
    content: str


class MemoryEntryResponse(BaseModel):
    id: int
    scope: str
    user_id: Optional[str] = None
    session_id: Optional[int] = None
    content: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
