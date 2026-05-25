import os
import time
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.logger import logger
from app.core.database import get_db
from app.core.ratelimit import limiter

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="SkinAI API",
    description="Backend para análisis cutáneo asistido por IA.",
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
allowed_origins = [
    o.strip()
    for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# ── Rate limiting ─────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ── Routers ───────────────────────────────────────────────────────────────────
from app.api import auth, users, analysis, routines, products

app.include_router(auth.router,      prefix="/api/auth",      tags=["auth"])
app.include_router(users.router,     prefix="/api/users",     tags=["users"])
app.include_router(analysis.router,  prefix="/api/analysis",  tags=["analysis"])
app.include_router(routines.router,  prefix="/api/routines",  tags=["routines"])
app.include_router(products.router,  prefix="/api/products",  tags=["products"])

# ── Security headers ──────────────────────────────────────────────────────────
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "frame-ancestors 'none';"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# ── Request logging ───────────────────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    logger.info("Request processed", extra={"extra": {
        "path":         request.url.path,
        "method":       request.method,
        "status_code":  response.status_code,
        "process_time": f"{time.time() - start_time:.4f}s",
    }})
    return response

# ── Health checks ─────────────────────────────────────────────────────────────
@app.get("/", tags=["health"])
def read_root():
    return {"service": "SkinAI API", "status": "ok"}

@app.get("/health/db", tags=["health"])
def check_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception:
        logger.error("Database health check failed", exc_info=True)
        return {"status": "error"}
