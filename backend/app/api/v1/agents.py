from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.core.response import success_response, error_response, ErrorCode
from app.core.deps import get_current_user
from app.models.user import User
from app.models.agent import Agent, RoleFile
from app.models.session import Session as SessionModel
from app.models.model_provider import AgentModelBinding
from app.models.skill import AgentSkillBinding
from app.models.knowledge_base import AgentKBBinding
from app.models.memory import MemoryConfig
from app.schemas.agent import *
from datetime import datetime

router = APIRouter(prefix="/agents", tags=["agents"])

FILE_TYPES = ["agent_md", "user_md", "identity_md", "soul_md"]


@router.get("")
def list_agents(
    status: Optional[str] = None,
    name: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    q = db.query(Agent).filter(Agent.status != "deleted")
    if status and status != "all":
        q = q.filter(Agent.status == status)
    if name:
        q = q.filter(Agent.name.ilike(f"%{name}%"))
    total = q.count()
    items = q.order_by(Agent.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success_response({
        "items": [
            {
                "id": a.id, "name": a.name, "description": a.description,
                "avatar": a.avatar, "status": a.status,
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "updated_at": a.updated_at.isoformat() if a.updated_at else None,
            }
            for a in items
        ],
        "total": total, "page": page, "page_size": page_size
    })


@router.post("")
def create_agent(req: AgentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    agent = Agent(name=req.name, description=req.description, avatar=req.avatar, status="draft")
    db.add(agent)
    db.flush()
    # Initialize 4 role files
    for ft in FILE_TYPES:
        rf = RoleFile(agent_id=agent.id, file_type=ft, content="", version=1, is_current=True, operator=user.username)
        db.add(rf)
    # Initialize memory config
    mc = MemoryConfig(agent_id=agent.id)
    db.add(mc)
    db.commit()
    db.refresh(agent)
    return success_response({
        "id": agent.id, "name": agent.name, "description": agent.description,
        "avatar": agent.avatar, "status": agent.status,
        "created_at": agent.created_at.isoformat() if agent.created_at else None
    })


@router.get("/{agent_id}")
def get_agent(agent_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.status != "deleted").first()
    if not agent:
        return error_response(*ErrorCode.NOT_FOUND, message="Agent 不存在")
    return success_response({
        "id": agent.id, "name": agent.name, "description": agent.description,
        "avatar": agent.avatar, "status": agent.status,
        "created_at": agent.created_at.isoformat() if agent.created_at else None,
        "updated_at": agent.updated_at.isoformat() if agent.updated_at else None,
    })


@router.put("/{agent_id}")
def update_agent(agent_id: int, req: AgentUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.status != "deleted").first()
    if not agent:
        return error_response(*ErrorCode.NOT_FOUND, message="Agent 不存在")
    if req.name is not None:
        agent.name = req.name
    if req.description is not None:
        agent.description = req.description
    if req.avatar is not None:
        agent.avatar = req.avatar
    db.commit()
    return success_response({"id": agent.id, "name": agent.name, "status": agent.status})


@router.delete("/{agent_id}")
def delete_agent(agent_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        return error_response(*ErrorCode.NOT_FOUND, message="Agent 不存在")
    if agent.status == "active":
        active_sessions = db.query(SessionModel).filter(
            SessionModel.agent_id == agent_id,
            SessionModel.status.in_(["running", "idle"])
        ).count()
        if active_sessions > 0:
            return error_response(*ErrorCode.STATE_CONFLICT, message=f"Agent 有 {active_sessions} 个活跃 Session，无法删除")
    agent.status = "deleted"
    db.commit()
    return success_response(message="已删除")


@router.patch("/{agent_id}/status")
def update_agent_status(agent_id: int, req: AgentStatusUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.status != "deleted").first()
    if not agent:
        return error_response(*ErrorCode.NOT_FOUND, message="Agent 不存在")
    if req.status == "active":
        # Validate: at least one model binding
        binding = db.query(AgentModelBinding).filter(AgentModelBinding.agent_id == agent_id).first()
        if not binding:
            return error_response(*ErrorCode.PARAM_ERROR, message="启用前需至少绑定一个模型")
        agent.status = "active"
    elif req.status == "inactive":
        if agent.status == "active":
            agent.status = "inactive"
    else:
        return error_response(*ErrorCode.PARAM_ERROR, message="不支持的状态")
    db.commit()
    return success_response({"id": agent.id, "status": agent.status})


@router.post("/{agent_id}/duplicate")
def duplicate_agent(agent_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.status != "deleted").first()
    if not agent:
        return error_response(*ErrorCode.NOT_FOUND, message="Agent 不存在")
    new_agent = Agent(name=f"{agent.name}_copy", description=agent.description, avatar=agent.avatar, status="draft")
    db.add(new_agent)
    db.flush()
    # Copy role files
    for rf in db.query(RoleFile).filter(RoleFile.agent_id == agent_id, RoleFile.is_current == True).all():
        new_rf = RoleFile(agent_id=new_agent.id, file_type=rf.file_type, content=rf.content, version=1, is_current=True, operator=user.username)
        db.add(new_rf)
    # Copy model binding
    mb = db.query(AgentModelBinding).filter(AgentModelBinding.agent_id == agent_id).first()
    if mb:
        new_mb = AgentModelBinding(agent_id=new_agent.id, provider_id=mb.provider_id, model_name=mb.model_name,
                                   temperature=mb.temperature, max_tokens=mb.max_tokens, top_p=mb.top_p)
        db.add(new_mb)
    # Copy skill bindings
    for sb in db.query(AgentSkillBinding).filter(AgentSkillBinding.agent_id == agent_id).all():
        new_sb = AgentSkillBinding(agent_id=new_agent.id, skill_id=sb.skill_id, enabled=sb.enabled)
        db.add(new_sb)
    # Copy KB bindings
    for kb in db.query(AgentKBBinding).filter(AgentKBBinding.agent_id == agent_id).all():
        new_kb = AgentKBBinding(agent_id=new_agent.id, kb_id=kb.kb_id, top_k=kb.top_k, similarity_threshold=kb.similarity_threshold)
        db.add(new_kb)
    # Copy memory config
    mc = db.query(MemoryConfig).filter(MemoryConfig.agent_id == agent_id).first()
    if mc:
        new_mc = MemoryConfig(agent_id=new_agent.id, agent_scope_enabled=mc.agent_scope_enabled,
                              user_scope_enabled=mc.user_scope_enabled, session_scope_enabled=mc.session_scope_enabled,
                              write_strategy=mc.write_strategy)
        db.add(new_mc)
    db.commit()
    db.refresh(new_agent)
    return success_response({"id": new_agent.id, "name": new_agent.name, "status": new_agent.status})


# ---- Role Files ----

@router.get("/{agent_id}/role-files")
def get_role_files(agent_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.status != "deleted").first()
    if not agent:
        return error_response(*ErrorCode.NOT_FOUND, message="Agent 不存在")
    result = {}
    for ft in FILE_TYPES:
        rf = db.query(RoleFile).filter(
            RoleFile.agent_id == agent_id, RoleFile.file_type == ft, RoleFile.is_current == True
        ).first()
        result[ft] = {
            "file_type": ft,
            "content": rf.content if rf else "",
            "version": rf.version if rf else 0,
            "is_current": True,
            "created_at": rf.created_at.isoformat() if rf and rf.created_at else None
        }
    return success_response(result)


@router.put("/{agent_id}/role-files/{file_type}")
def update_role_file(agent_id: int, file_type: str, req: RoleFileUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if file_type not in FILE_TYPES:
        return error_response(*ErrorCode.PARAM_ERROR, message="不支持的角色文件类型")
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.status != "deleted").first()
    if not agent:
        return error_response(*ErrorCode.NOT_FOUND, message="Agent 不存在")
    # Mark old current as non-current
    old = db.query(RoleFile).filter(
        RoleFile.agent_id == agent_id, RoleFile.file_type == file_type, RoleFile.is_current == True
    ).first()
    old_version = old.version if old else 0
    if old:
        old.is_current = False
    # Create new version
    new_rf = RoleFile(agent_id=agent_id, file_type=file_type, content=req.content,
                      version=old_version + 1, is_current=True, operator=req.operator or user.username)
    db.add(new_rf)
    db.commit()
    return success_response({"file_type": file_type, "version": new_rf.version, "is_current": True})


@router.get("/{agent_id}/role-files/{file_type}/versions")
def get_role_file_versions(agent_id: int, file_type: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if file_type not in FILE_TYPES:
        return error_response(*ErrorCode.PARAM_ERROR, message="不支持的角色文件类型")
    versions = db.query(RoleFile).filter(
        RoleFile.agent_id == agent_id, RoleFile.file_type == file_type
    ).order_by(RoleFile.version.desc()).all()
    return success_response([
        {
            "id": v.id, "version": v.version, "is_current": v.is_current,
            "created_at": v.created_at.isoformat() if v.created_at else None,
            "operator": v.operator
        }
        for v in versions
    ])


@router.post("/{agent_id}/role-files/{file_type}/versions/{version}/restore")
def restore_role_file_version(agent_id: int, file_type: str, version: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if file_type not in FILE_TYPES:
        return error_response(*ErrorCode.PARAM_ERROR, message="不支持的角色文件类型")
    target = db.query(RoleFile).filter(
        RoleFile.agent_id == agent_id, RoleFile.file_type == file_type, RoleFile.version == version
    ).first()
    if not target:
        return error_response(*ErrorCode.NOT_FOUND, message="版本不存在")
    # Mark all as non-current
    db.query(RoleFile).filter(
        RoleFile.agent_id == agent_id, RoleFile.file_type == file_type
    ).update({RoleFile.is_current: False})
    # Get max version
    max_version = db.query(RoleFile).filter(
        RoleFile.agent_id == agent_id, RoleFile.file_type == file_type
    ).count()
    # Create new version based on target content
    new_rf = RoleFile(agent_id=agent_id, file_type=file_type, content=target.content,
                      version=max_version + 1, is_current=True, operator=user.username)
    db.add(new_rf)
    db.commit()
    return success_response({"file_type": file_type, "version": new_rf.version, "is_current": True})
