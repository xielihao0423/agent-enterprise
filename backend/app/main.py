from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import get_settings
from app.db.session import init_db, SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.api.v1 import api_router

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, debug=settings.DEBUG)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    # Create default admin user if not exists
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == settings.DEFAULT_ADMIN_USERNAME).first()
        if not admin:
            admin = User(
                username=settings.DEFAULT_ADMIN_USERNAME,
                hashed_password=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
                display_name="Administrator"
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": f"服务器内部错误: {str(exc)}", "data": None}
    )


app.include_router(api_router)


@app.get("/")
def root():
    return {"code": 0, "message": "success", "data": {"name": settings.APP_NAME, "version": settings.APP_VERSION}}


@app.get("/health")
def health():
    return {"code": 0, "message": "success", "data": {"status": "healthy"}}
