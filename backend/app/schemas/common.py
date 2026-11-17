from pydantic import BaseModel
from typing import Any, Optional, List, Generic, TypeVar
from datetime import datetime

T = TypeVar("T")


class ResponseBase(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20


class PaginatedResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[dict] = None
