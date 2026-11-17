from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ModelProviderCreate(BaseModel):
    provider_type: str  # ark/openai
    name: str
    api_key: str
    base_url: Optional[str] = None
    available_models: Optional[List[str]] = []


class ModelProviderUpdate(BaseModel):
    name: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    available_models: Optional[List[str]] = None


class ModelProviderResponse(BaseModel):
    id: int
    provider_type: str
    name: str
    api_key_masked: str
    base_url: Optional[str] = None
    available_models: List[str] = []
    status: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AgentModelBindingUpdate(BaseModel):
    provider_id: int
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 0.9


class AgentModelBindingResponse(BaseModel):
    provider_id: int
    model_name: str
    temperature: float
    max_tokens: int
    top_p: float
    
    class Config:
        from_attributes = True
