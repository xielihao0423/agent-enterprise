from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.response import success_response, error_response, ErrorCode
from app.core.security import encrypt_credential, decrypt_credential, mask_credential
from app.core.deps import get_current_user
from app.models.user import User
from app.models.feishu_bot import FeishuBot
from app.schemas.feishu import *

router = APIRouter(prefix="/feishu-bots", tags=["feishu-bots"])


@router.get("")
def list_bots(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bots = db.query(FeishuBot).all()
    return success_response([{
        "id": b.id, "name": b.name, "app_id": b.app_id,
        "app_secret_masked": mask_credential(decrypt_credential(b.app_secret_encrypted)),
        "agent_id": b.agent_id, "connection_mode": b.connection_mode,
        "status": b.status,
        "created_at": b.created_at.isoformat() if b.created_at else None
    } for b in bots])


@router.post("")
def create_bot(req: FeishuBotCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bot = FeishuBot(
        name=req.name, app_id=req.app_id,
        app_secret_encrypted=encrypt_credential(req.app_secret),
        connection_mode=req.connection_mode, status="disconnected"
    )
    db.add(bot)
    db.commit()
    db.refresh(bot)
    return success_response({"id": bot.id, "name": bot.name, "status": bot.status})


@router.put("/{bot_id}/agent")
def bind_agent(bot_id: int, req: FeishuBotBindAgent, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bot = db.query(FeishuBot).filter(FeishuBot.id == bot_id).first()
    if not bot:
        return error_response(*ErrorCode.NOT_FOUND, message="机器人不存在")
    bot.agent_id = req.agent_id
    db.commit()
    return success_response({"bot_id": bot_id, "agent_id": req.agent_id})


@router.get("/{bot_id}/status")
def get_bot_status(bot_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bot = db.query(FeishuBot).filter(FeishuBot.id == bot_id).first()
    if not bot:
        return error_response(*ErrorCode.NOT_FOUND, message="机器人不存在")
    return success_response({"bot_id": bot_id, "status": bot.status, "connection_mode": bot.connection_mode})
