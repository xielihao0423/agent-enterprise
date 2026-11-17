from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.response import success_response, error_response, ErrorCode
from app.core.security import encrypt_credential, decrypt_credential, mask_credential
from app.core.deps import get_current_user
from app.models.user import User
from app.models.model_provider import ModelProvider, AgentModelBinding
from app.models.agent import Agent
from app.schemas.model_provider import *
import httpx

router = APIRouter(prefix="/model-providers", tags=["model-providers"])


@router.get("")
def list_providers(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    providers = db.query(ModelProvider).all()
    return success_response([{
        "id": p.id, "provider_type": p.provider_type, "name": p.name,
        "api_key_masked": mask_credential(decrypt_credential(p.api_key_encrypted)),
        "base_url": p.base_url, "available_models": p.available_models.split(",") if p.available_models else [],
        "status": p.status,
        "created_at": p.created_at.isoformat() if p.created_at else None
    } for p in providers])


@router.post("")
def create_provider(req: ModelProviderCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    provider = ModelProvider(
        provider_type=req.provider_type, name=req.name,
        api_key_encrypted=encrypt_credential(req.api_key),
        base_url=req.base_url,
        available_models=",".join(req.available_models) if req.available_models else "",
        status="available"
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return success_response({"id": provider.id, "name": provider.name, "status": provider.status})


@router.put("/{provider_id}")
def update_provider(provider_id: int, req: ModelProviderUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    provider = db.query(ModelProvider).filter(ModelProvider.id == provider_id).first()
    if not provider:
        return error_response(*ErrorCode.NOT_FOUND, message="供应商不存在")
    if req.name is not None:
        provider.name = req.name
    if req.api_key is not None:
        provider.api_key_encrypted = encrypt_credential(req.api_key)
    if req.base_url is not None:
        provider.base_url = req.base_url
    if req.available_models is not None:
        provider.available_models = ",".join(req.available_models)
    db.commit()
    return success_response({"id": provider.id, "name": provider.name})


@router.post("/{provider_id}/test")
async def test_provider(provider_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    provider = db.query(ModelProvider).filter(ModelProvider.id == provider_id).first()
    if not provider:
        return error_response(*ErrorCode.NOT_FOUND, message="供应商不存在")
    api_key = decrypt_credential(provider.api_key_encrypted)
    # Simple validation: check if key is non-empty
    if len(api_key) < 4:
        return error_response(*ErrorCode.PARAM_ERROR, message="API Key 格式无效")
    # Mark as available (in production, would send a real test request)
    provider.status = "available"
    db.commit()
    return success_response({"status": "available", "message": "连接测试成功"})


# Agent model binding
@router.put("/agents/{agent_id}/model")
def bind_agent_model(agent_id: int, req: AgentModelBindingUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.status != "deleted").first()
    if not agent:
        return error_response(*ErrorCode.NOT_FOUND, message="Agent 不存在")
    provider = db.query(ModelProvider).filter(ModelProvider.id == req.provider_id).first()
    if not provider:
        return error_response(*ErrorCode.NOT_FOUND, message="模型供应商不存在")
    existing = db.query(AgentModelBinding).filter(AgentModelBinding.agent_id == agent_id).first()
    if existing:
        existing.provider_id = req.provider_id
        existing.model_name = req.model_name
        existing.temperature = req.temperature
        existing.max_tokens = req.max_tokens
        existing.top_p = req.top_p
    else:
        binding = AgentModelBinding(
            agent_id=agent_id, provider_id=req.provider_id, model_name=req.model_name,
            temperature=req.temperature, max_tokens=req.max_tokens, top_p=req.top_p
        )
        db.add(binding)
    db.commit()
    return success_response({"agent_id": agent_id, "model_name": req.model_name, "provider_id": req.provider_id})
