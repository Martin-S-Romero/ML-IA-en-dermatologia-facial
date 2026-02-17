import time
from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.logger import logger
from app.core.database import engine, Base, get_db
from app.core.ratelimit import limiter
from app import models

# Create tables on startup
# Retry logic for DB connection
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

app = FastAPI()

# Rate Limiting Setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

from app.api import auth, upload, process
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(process.router, prefix="/process", tags=["process"])

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    log_data = {
        "path": request.url.path,
        "method": request.method,
        "status_code": response.status_code,
        "process_time": f"{process_time:.4f}s"
    }
    
    logger.info("Request processed", extra={"extra": log_data})
    return response

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Hello from Backend with Logs", "db_status": "connected"}

@app.get("/health/db")
def check_db(db: Session = Depends(get_db)):
    try:
        # Try to execute a simple query
        result = db.execute(text("SELECT 1"))
        return {"status": "ok", "result": result.scalar()}
    except Exception as e:
        logger.error("Database connection failed", exc_info=True)
        return {"status": "error", "message": str(e)}

@app.get("/test-error")
def test_error():
    try:
        1 / 0
    except Exception as e:
        logger.error("Intentional error triggered", exc_info=True)
        return {"error": "Intentional error triggered"}
