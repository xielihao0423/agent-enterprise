from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class KBCreate(BaseModel):
    name: str
    description: Optional[str] = None


class KBResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    document_count: int = 0
    
    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: int
    kb_id: int
    filename: str
    file_size: int = 0
    status: str
    error_reason: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AgentKBBind(BaseModel):
    kb_id: int
    top_k: int = 3
    similarity_threshold: float = 0.7


class AgentKBBindingResponse(BaseModel):
    id: int
    kb_id: int
    kb_name: str
    top_k: int
    similarity_threshold: float
    
    class Config:
        from_attributes = True
