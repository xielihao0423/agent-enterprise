from fastapi.responses import JSONResponse
from typing import Any, Optional


def success_response(data: Any = None, message: str = "success", status_code: int = 200):
    return {"code": 0, "message": message, "data": data}


def error_response(code: int, message: str, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content={"code": code, "message": message, "data": None}
    )


class ErrorCode:
    PARAM_ERROR = (1001, 400)
    UNAUTHORIZED = (1002, 401)
    FORBIDDEN = (1003, 403)
    NOT_FOUND = (1004, 404)
    STATE_CONFLICT = (1005, 409)
    MODEL_ERROR = (2001, 500)
    SKILL_ERROR = (2002, 500)
    KB_TIMEOUT = (2003, 500)
    FEISHU_ERROR = (2004, 503)
