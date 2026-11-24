from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SkillCreate(BaseModel):
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    source: Optional[str] = None


class SkillResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    version: str
    source: Optional[str] = None
    installed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AgentSkillBind(BaseModel):
    skill_id: int


class AgentSkillBindingResponse(BaseModel):
    id: int
    skill_id: int
    skill_name: str
    skill_version: str
    enabled: bool
    bound_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SkillToggleUpdate(BaseModel):
    enabled: bool
