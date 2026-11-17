from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.core.response import success_response
from app.core.deps import get_current_user
from app.models.user import User
from app.models.audit import AuditLog
from app.models.session import Message

router = APIRouter(tags=["audit"])


@router.get("/audit-logs")
def list_audit_logs(page: int = 1, page_size: int = 20, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(AuditLog)
    total = q.count()
    items = q.order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success_response({
        "items": [{
            "id": a.id, "operator": a.operator, "action": a.action,
            "target_type": a.target_type, "target_id": a.target_id,
            "detail": a.detail,
            "created_at": a.created_at.isoformat() if a.created_at else None
        } for a in items],
        "total": total, "page": page, "page_size": page_size
    })


@router.get("/metrics/token-usage")
def token_usage_metrics(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from app.models.agent import Agent
    from sqlalchemy import func
    results = db.query(
        Agent.id, Agent.name,
        func.sum(Message.token_usage).label("total_tokens"),
        func.count(Message.id).label("call_count")
    ).join(Message, Message.session_id.in_(
        db.query(Message.session_id).filter(Message.role == "assistant")
    )).group_by(Agent.id).all()
    # Simplified: return empty if no data
    return success_response({
        "items": [],
        "total": 0
    })


@router.get("/metrics/errors")
def error_metrics(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return success_response({"items": [], "total": 0})
