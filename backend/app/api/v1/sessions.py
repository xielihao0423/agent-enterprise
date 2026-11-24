from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.response import success_response, error_response, ErrorCode
from app.core.deps import get_current_user
from app.models.user import User
from app.models.session import Session as SessionModel, Message
from app.models.agent import Agent
from app.schemas.session import *
from app.services import agent_runtime

router = APIRouter(tags=["sessions"])


@router.get("/agents/{agent_id}/sessions")
def list_sessions(agent_id: int, page: int = 1, page_size: int = 20, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(SessionModel).filter(SessionModel.agent_id == agent_id)
    total = q.count()
    items = q.order_by(SessionModel.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for s in items:
        msg_count = db.query(Message).filter(Message.session_id == s.id).count()
        result.append({
            "id": s.id, "agent_id": s.agent_id, "user_id": s.user_id,
            "source": s.source, "chat_type": s.chat_type, "chat_id": s.chat_id,
            "status": s.status,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            "message_count": msg_count
        })
    return success_response({"items": result, "total": total, "page": page, "page_size": page_size})


@router.post("/agents/{agent_id}/sessions")
def create_session(agent_id: int, req: SessionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.status == "active").first()
    if not agent:
        return error_response(*ErrorCode.NOT_FOUND, message="Agent 不存在或未启用")
    session = SessionModel(
        agent_id=agent_id, user_id=req.user_id, source=req.source,
        chat_type=req.chat_type, chat_id=req.chat_id, status="idle"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return success_response({
        "id": session.id, "agent_id": session.agent_id, "status": session.status,
        "created_at": session.created_at.isoformat() if session.created_at else None
    })


@router.get("/sessions/{session_id}")
def get_session(session_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not s:
        return error_response(*ErrorCode.NOT_FOUND, message="Session 不存在")
    return success_response({
        "id": s.id, "agent_id": s.agent_id, "user_id": s.user_id,
        "source": s.source, "chat_type": s.chat_type, "chat_id": s.chat_id,
        "status": s.status,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "updated_at": s.updated_at.isoformat() if s.updated_at else None
    })


@router.get("/sessions/{session_id}/messages")
def list_messages(session_id: int, page: int = 1, page_size: int = 50, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Message).filter(Message.session_id == session_id)
    total = q.count()
    items = q.order_by(Message.created_at.asc()).offset((page - 1) * page_size).limit(page_size).all()
    return success_response({
        "items": [{
            "id": m.id, "session_id": m.session_id, "role": m.role,
            "content": m.content, "attachments": m.attachments,
            "token_usage": m.token_usage, "tool_calls": m.tool_calls,
            "created_at": m.created_at.isoformat() if m.created_at else None
        } for m in items],
        "total": total, "page": page, "page_size": page_size
    })


@router.post("/sessions/{session_id}/messages")
def send_message(session_id: int, req: MessageCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not s:
        return error_response(*ErrorCode.NOT_FOUND, message="Session 不存在")
    if s.status == "closed":
        return error_response(*ErrorCode.STATE_CONFLICT, message="Session 已关闭")
    agent = db.query(Agent).filter(Agent.id == s.agent_id).first()
    if not agent:
        return error_response(*ErrorCode.NOT_FOUND, message="Agent 不存在")

    # Save user message first so it is never lost, then execute the real runtime.
    user_msg = Message(session_id=session_id, role="user", content=req.content, attachments=req.attachments)
    db.add(user_msg)
    s.status = "running"
    db.commit()

    # Load prior context (exclude the just-saved user message; it is passed explicitly).
    history = [
        {"role": m.role, "content": m.content}
        for m in db.query(Message)
        .filter(Message.session_id == session_id, Message.id != user_msg.id)
        .order_by(Message.created_at.asc())
        .all()
        if m.role in ("user", "assistant")
    ]

    try:
        result = agent_runtime.run_agent(db, agent, s, req.content, history=history)
    except agent_runtime.AgentRuntimeError as exc:
        # Execution failed: record the error, reset session state, surface a real error.
        s.status = "idle"
        db.commit()
        return error_response(*ErrorCode.MODEL_ERROR, message=str(exc))
    except Exception as exc:  # noqa: BLE001
        s.status = "idle"
        db.commit()
        return error_response(*ErrorCode.MODEL_ERROR, message=f"Agent 执行异常: {exc}")

    assistant_msg = Message(
        session_id=session_id, role="assistant",
        content=result.content, token_usage=result.token_usage, tool_calls=result.tool_calls
    )
    db.add(assistant_msg)
    s.status = "idle"
    db.commit()
    db.refresh(assistant_msg)
    return success_response({
        "id": assistant_msg.id, "session_id": session_id, "role": "assistant",
        "content": assistant_msg.content, "token_usage": assistant_msg.token_usage,
        "tool_calls": assistant_msg.tool_calls,
        "created_at": assistant_msg.created_at.isoformat() if assistant_msg.created_at else None
    })


@router.post("/sessions/{session_id}/interrupt")
def interrupt_session(session_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not s:
        return error_response(*ErrorCode.NOT_FOUND, message="Session 不存在")
    if s.status != "running":
        return error_response(*ErrorCode.STATE_CONFLICT, message="Session 当前状态不支持中断")
    s.status = "interrupted"
    db.commit()
    return success_response({"id": s.id, "status": s.status})


@router.post("/sessions/{session_id}/resume")
def resume_session(session_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not s:
        return error_response(*ErrorCode.NOT_FOUND, message="Session 不存在")
    if s.status != "interrupted":
        return error_response(*ErrorCode.STATE_CONFLICT, message="Session 当前状态不支持续跑")
    # Resuming simply re-opens the session for further messages; execution
    # happens on the next send_message call through the real runtime.
    s.status = "idle"
    db.commit()
    return success_response({"id": s.id, "status": s.status})


@router.patch("/sessions/{session_id}/status")
def update_session_status(session_id: int, req: SessionStatusUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not s:
        return error_response(*ErrorCode.NOT_FOUND, message="Session 不存在")
    if req.status == "closed":
        if s.status not in ("idle", "interrupted"):
            return error_response(*ErrorCode.STATE_CONFLICT, message="Session 当前状态不支持关闭")
        s.status = "closed"
    db.commit()
    return success_response({"id": s.id, "status": s.status})


@router.get("/sessions/{session_id}/traces")
def get_traces(session_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    messages = db.query(Message).filter(Message.session_id == session_id).all()
    traces = []
    for m in messages:
        if m.tool_calls:
            traces.append({
                "message_id": m.id, "role": m.role,
                "tool_calls": m.tool_calls,
                "token_usage": m.token_usage,
                "created_at": m.created_at.isoformat() if m.created_at else None
            })
    return success_response({"items": traces, "total": len(traces)})
