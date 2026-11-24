from fastapi.responses import JSONResponse
from typing import Any, Optional


def success_response(data: Any = None, message: str = "success", status_code: int = 200):
    return {"code": 0, "message": message, "data": data}


def error_response(*args, message=None):
    """Build an error JSONResponse.

    Supported call patterns:
      1. error_response(code, "message text", http_status)  -- positional
      2. error_response(*ErrorCode.X, message="text")       -- unpacked tuple
         where ErrorCode.X == (code, http_status)

    Pattern 2 is used across all API routes:
      error_response(*ErrorCode.NOT_FOUND, message="Agent 不存在")
      expands to error_response(1004, 404, message="Agent 不存在"),
      so args == (1004, 404) and the message arrives as a keyword.
    """
    if len(args) == 2 and message is not None:
        # Pattern 2: args = (error_code, http_status)
        code, http_status = args
    else:
        # Pattern 1: args = (code, [message, [http_status]])
        code = args[0] if args else 0
        http_status = 400
        if len(args) > 2 and isinstance(args[2], int):
            http_status = args[2]
        if message is None and len(args) > 1 and isinstance(args[1], str):
            message = args[1]

    return JSONResponse(
        status_code=http_status,
        content={"code": code, "message": message or "", "data": None}
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
