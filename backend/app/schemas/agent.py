from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    avatar: Optional[str] = None


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    avatar: Optional[str] = None


class AgentStatusUpdate(BaseModel):
    status: str  # active/inactive


class AgentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    avatar: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RoleFileUpdate(BaseModel):
    content: str
    operator: Optional[str] = "admin"


class RoleFileResponse(BaseModel):
    file_type: str
    content: str
    version: int
    is_current: bool
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RoleFileVersionResponse(BaseModel):
    id: int
    version: int
    is_current: bool
    created_at: Optional[datetime] = None
    operator: Optional[str] = None
    
    class Config:
        from_attributes = True
