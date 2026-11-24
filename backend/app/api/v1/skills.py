from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.response import success_response, error_response, ErrorCode
from app.core.deps import get_current_user
from app.models.user import User
from app.models.skill import Skill, AgentSkillBinding
from app.models.agent import Agent
from app.schemas.skill import *

router = APIRouter(tags=["skills"])


@router.get("/skills")
def list_skills(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    skills = db.query(Skill).all()
    return success_response([{
        "id": s.id, "name": s.name, "description": s.description,
        "version": s.version, "source": s.source,
        "installed_at": s.installed_at.isoformat() if s.installed_at else None
    } for s in skills])


@router.post("/skills")
def install_skill(req: SkillCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    skill = Skill(name=req.name, description=req.description, version=req.version, source=req.source)
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return success_response({"id": skill.id, "name": skill.name, "version": skill.version})


@router.post("/agents/{agent_id}/skills")
def bind_skill(agent_id: int, req: AgentSkillBind, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.status != "deleted").first()
    if not agent:
        return error_response(*ErrorCode.NOT_FOUND, message="Agent 不存在")
    skill = db.query(Skill).filter(Skill.id == req.skill_id).first()
    if not skill:
        return error_response(*ErrorCode.NOT_FOUND, message="Skill 不存在")
    existing = db.query(AgentSkillBinding).filter(
        AgentSkillBinding.agent_id == agent_id, AgentSkillBinding.skill_id == req.skill_id
    ).first()
    if existing:
        return error_response(*ErrorCode.STATE_CONFLICT, message="Skill 已绑定")
    binding = AgentSkillBinding(agent_id=agent_id, skill_id=req.skill_id, enabled=True)
    db.add(binding)
    db.commit()
    return success_response({"agent_id": agent_id, "skill_id": req.skill_id, "enabled": True})


@router.delete("/agents/{agent_id}/skills/{skill_id}")
def unbind_skill(agent_id: int, skill_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    binding = db.query(AgentSkillBinding).filter(
        AgentSkillBinding.agent_id == agent_id, AgentSkillBinding.skill_id == skill_id
    ).first()
    if not binding:
        return error_response(*ErrorCode.NOT_FOUND, message="绑定关系不存在")
    db.delete(binding)
    db.commit()
    return success_response(message="已解绑")


@router.patch("/agents/{agent_id}/skills/{skill_id}")
def toggle_skill(agent_id: int, skill_id: int, req: SkillToggleUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    binding = db.query(AgentSkillBinding).filter(
        AgentSkillBinding.agent_id == agent_id, AgentSkillBinding.skill_id == skill_id
    ).first()
    if not binding:
        return error_response(*ErrorCode.NOT_FOUND, message="绑定关系不存在")
    binding.enabled = req.enabled
    db.commit()
    return success_response({"agent_id": agent_id, "skill_id": skill_id, "enabled": req.enabled})
