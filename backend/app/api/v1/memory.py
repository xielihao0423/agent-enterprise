from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.core.response import success_response, error_response, ErrorCode
from app.core.deps import get_current_user
from app.models.user import User
from app.models.memory import MemoryConfig, MemoryEntry
from app.models.agent import Agent
from app.schemas.memory import *

router = APIRouter(tags=["memory"])


@router.get("/agents/{agent_id}/memory-config")
def get_memory_config(agent_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    config = db.query(MemoryConfig).filter(MemoryConfig.agent_id == agent_id).first()
    if not config:
        return success_response({
            "agent_scope_enabled": False, "user_scope_enabled": False,
            "session_scope_enabled": False, "write_strategy": "auto"
        })
    return success_response({
        "agent_scope_enabled": config.agent_scope_enabled,
        "user_scope_enabled": config.user_scope_enabled,
        "session_scope_enabled": config.session_scope_enabled,
        "write_strategy": config.write_strategy
    })


@router.put("/agents/{agent_id}/memory-config")
def update_memory_config(agent_id: int, req: MemoryConfigUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    config = db.query(MemoryConfig).filter(MemoryConfig.agent_id == agent_id).first()
    if not config:
        config = MemoryConfig(agent_id=agent_id)
        db.add(config)
    if req.agent_scope_enabled is not None:
        config.agent_scope_enabled = req.agent_scope_enabled
    if req.user_scope_enabled is not None:
        config.user_scope_enabled = req.user_scope_enabled
    if req.session_scope_enabled is not None:
        config.session_scope_enabled = req.session_scope_enabled
    if req.write_strategy is not None:
        config.write_strategy = req.write_strategy
    db.commit()
    return success_response({
        "agent_scope_enabled": config.agent_scope_enabled,
        "user_scope_enabled": config.user_scope_enabled,
        "session_scope_enabled": config.session_scope_enabled,
        "write_strategy": config.write_strategy
    })


@router.get("/agents/{agent_id}/memories")
def list_memories(
    agent_id: int,
    scope: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    q = db.query(MemoryEntry).filter(MemoryEntry.agent_id == agent_id)
    if scope:
        q = q.filter(MemoryEntry.scope == scope)
    if user_id:
        q = q.filter(MemoryEntry.user_id == user_id)
    if session_id:
        q = q.filter(MemoryEntry.session_id == session_id)
    total = q.count()
    items = q.order_by(MemoryEntry.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success_response({
        "items": [{
            "id": m.id, "scope": m.scope, "user_id": m.user_id,
            "session_id": m.session_id, "content": m.content,
            "created_at": m.created_at.isoformat() if m.created_at else None
        } for m in items],
        "total": total, "page": page, "page_size": page_size
    })


@router.delete("/agents/{agent_id}/memories/{memory_id}")
def delete_memory(agent_id: int, memory_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    entry = db.query(MemoryEntry).filter(MemoryEntry.id == memory_id, MemoryEntry.agent_id == agent_id).first()
    if not entry:
        return error_response(*ErrorCode.NOT_FOUND, message="记忆条目不存在")
    db.delete(entry)
    db.commit()
    return success_response(message="已删除")


@router.delete("/agents/{agent_id}/memories")
def batch_delete_memories(
    agent_id: int,
    scope: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    q = db.query(MemoryEntry).filter(MemoryEntry.agent_id == agent_id)
    if scope:
        q = q.filter(MemoryEntry.scope == scope)
    count = q.count()
    q.delete()
    db.commit()
    return success_response({"deleted_count": count})
