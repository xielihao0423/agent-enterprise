import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.response import success_response, error_response, ErrorCode
from app.core.deps import get_current_user
from app.models.user import User
from app.models.knowledge_base import KnowledgeBase, Document, AgentKBBinding
from app.models.agent import Agent
from app.schemas.knowledge_base import *

router = APIRouter(tags=["knowledge-bases"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/knowledge-bases")
def list_kbs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    kbs = db.query(KnowledgeBase).all()
    result = []
    for kb in kbs:
        doc_count = db.query(Document).filter(Document.kb_id == kb.id).count()
        result.append({
            "id": kb.id, "name": kb.name, "description": kb.description,
            "created_at": kb.created_at.isoformat() if kb.created_at else None,
            "document_count": doc_count
        })
    return success_response(result)


@router.post("/knowledge-bases")
def create_kb(req: KBCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    kb = KnowledgeBase(name=req.name, description=req.description)
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return success_response({"id": kb.id, "name": kb.name})


@router.get("/knowledge-bases/{kb_id}/documents")
def list_documents(kb_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    docs = db.query(Document).filter(Document.kb_id == kb_id).all()
    return success_response([{
        "id": d.id, "kb_id": d.kb_id, "filename": d.filename,
        "file_size": d.file_size, "status": d.status, "error_reason": d.error_reason,
        "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None
    } for d in docs])


@router.post("/knowledge-bases/{kb_id}/documents")
async def upload_document(kb_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not kb:
        return error_response(*ErrorCode.NOT_FOUND, message="知识库不存在")
    content = await file.read()
    file_ext = os.path.splitext(file.filename or "unknown.txt")[1]
    saved_name = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, saved_name)
    with open(file_path, "wb") as f:
        f.write(content)
    doc = Document(kb_id=kb_id, filename=file.filename, file_path=file_path,
                   file_size=len(content), status="ready")
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return success_response({"id": doc.id, "filename": doc.filename, "status": doc.status})


@router.post("/agents/{agent_id}/knowledge-bases")
def bind_kb(agent_id: int, req: AgentKBBind, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.status != "deleted").first()
    if not agent:
        return error_response(*ErrorCode.NOT_FOUND, message="Agent 不存在")
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == req.kb_id).first()
    if not kb:
        return error_response(*ErrorCode.NOT_FOUND, message="知识库不存在")
    existing = db.query(AgentKBBinding).filter(
        AgentKBBinding.agent_id == agent_id, AgentKBBinding.kb_id == req.kb_id
    ).first()
    if existing:
        existing.top_k = req.top_k
        existing.similarity_threshold = req.similarity_threshold
    else:
        binding = AgentKBBinding(agent_id=agent_id, kb_id=req.kb_id,
                                 top_k=req.top_k, similarity_threshold=req.similarity_threshold)
        db.add(binding)
    db.commit()
    return success_response({"agent_id": agent_id, "kb_id": req.kb_id, "top_k": req.top_k, "similarity_threshold": req.similarity_threshold})


@router.delete("/agents/{agent_id}/knowledge-bases/{kb_id}")
def unbind_kb(agent_id: int, kb_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    binding = db.query(AgentKBBinding).filter(
        AgentKBBinding.agent_id == agent_id, AgentKBBinding.kb_id == kb_id
    ).first()
    if not binding:
        return error_response(*ErrorCode.NOT_FOUND, message="绑定关系不存在")
    db.delete(binding)
    db.commit()
    return success_response(message="已解绑")
