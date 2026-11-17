from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.security import decode_access_token
from app.models.user import User


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={"code": 1002, "message": "未认证", "data": None})
    token = auth_header[7:]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail={"code": 1002, "message": "Token 无效或已过期", "data": None})
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail={"code": 1002, "message": "用户不存在", "data": None})
    return user
