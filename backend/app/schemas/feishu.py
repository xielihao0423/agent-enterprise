from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FeishuBotCreate(BaseModel):
    name: str
    app_id: str
    app_secret: str
    connection_mode: str = "long_polling"


class FeishuBotUpdate(BaseModel):
    name: Optional[str] = None
    app_id: Optional[str] = None
    app_secret: Optional[str] = None
    connection_mode: Optional[str] = None


class FeishuBotResponse(BaseModel):
    id: int
    name: str
    app_id: str
    app_secret_masked: str
    agent_id: Optional[int] = None
    connection_mode: str
    status: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class FeishuBotBindAgent(BaseModel):
    agent_id: int
