import time
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.logger import logger
from app.core.database import engine, Base, get_db
from app.core.ratelimit import limiter
from app import models

# ── Crear tablas en BD al iniciar (con reintentos) ────────────────────────
max_retries = 10
retry_delay = 2

for i in range(max_retries):
    try:
        models.Base.metadata.create_all(bind=engine)
        logger.info("Database connection successful and tables created.")
        break
    except Exception as e:
        if i == max_retries - 1:
            logger.error(f"Could not connect to database after {max_retries} attempts.", exc_info=True)
            raise e
        logger.warning(f"Database not ready yet, retrying in {retry_delay}s... ({i+1}/{max_retries})")
        time.sleep(retry_delay)

# ── App ───────────────────────────────────────────────────────────────────
app = FastAPI(
    title="SkinAI API",
    description="Backend para análisis cutáneo asistido por IA.",
    version="1.0.0",
)

# CORS — permite llamadas desde el frontend Vite en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ── Routers ───────────────────────────────────────────────────────────────
from app.api import auth, users, analysis, routines, products

app.include_router(auth.router,      prefix="/api/auth",      tags=["auth"])
app.include_router(users.router,     prefix="/api/users",     tags=["users"])
app.include_router(analysis.router,  prefix="/api/analysis",  tags=["analysis"])
app.include_router(routines.router,  prefix="/api/routines",  tags=["routines"])
app.include_router(products.router,  prefix="/api/products",  tags=["products"])

# ── Middleware de logs ────────────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response   = await call_next(request)
    process_time = time.time() - start_time

    logger.info("Request processed", extra={"extra": {
        "path":         request.url.path,
        "method":       request.method,
        "status_code":  response.status_code,
        "process_time": f"{process_time:.4f}s",
    }})
    return response

# ── Health checks ─────────────────────────────────────────────────────────
@app.get("/", tags=["health"])
def read_root():
    return {"service": "SkinAI API", "status": "ok"}

@app.get("/health/db", tags=["health"])
def check_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        logger.error("Database health check failed", exc_info=True)
        return {"status": "error", "message": str(e)}
