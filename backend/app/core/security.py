from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
import bcrypt
from cryptography.fernet import Fernet
import base64
import hashlib

from app.core.config import get_settings

settings = get_settings()


def _get_fernet() -> Fernet:
    """Get Fernet instance from encryption key."""
    key = settings.ENCRYPTION_KEY
    try:
        return Fernet(key.encode() if isinstance(key, str) else key)
    except Exception:
        derived = base64.urlsafe_b64encode(hashlib.sha256(key.encode()).digest())
        return Fernet(derived)


def encrypt_credential(plain_text: str) -> str:
    """Encrypt a credential string."""
    f = _get_fernet()
    return f.encrypt(plain_text.encode()).decode()


def decrypt_credential(encrypted: str) -> str:
    """Decrypt a credential string."""
    f = _get_fernet()
    return f.decrypt(encrypted.encode()).decode()


def mask_credential(plain_text: str, visible_chars: int = 4) -> str:
    """Mask a credential, showing only the last N characters."""
    if len(plain_text) <= visible_chars:
        return "****"
    return f"****{plain_text[-visible_chars:]}"


def hash_password(password: str) -> str:
    """Hash a password using bcrypt directly."""
    pwd_bytes = password.encode("utf-8")
    # bcrypt has a 72-byte limit
    if len(pwd_bytes) > 72:
        pwd_bytes = pwd_bytes[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against a bcrypt hash."""
    pwd_bytes = plain.encode("utf-8")
    if len(pwd_bytes) > 72:
        pwd_bytes = pwd_bytes[:72]
    try:
        return bcrypt.checkpw(pwd_bytes, hashed.encode("utf-8"))
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
