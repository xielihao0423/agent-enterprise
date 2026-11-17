from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.core.response import success_response, error_response, ErrorCode
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserInfo

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.hashed_password):
        return error_response(*ErrorCode.UNAUTHORIZED, message="用户名或密码错误")
    token = create_access_token({"sub": str(user.id), "username": user.username})
    return success_response({"access_token": token, "token_type": "bearer"})


@router.post("/logout")
def logout():
    return success_response(message="已登出")


@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return success_response({
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name
    })
