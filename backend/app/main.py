import time
from fastapi import FastAPI, Request
from app.core.logger import logger

app = FastAPI()

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
    return {"message": "Hello from Backend with Logs"}

@app.get("/test-error")
def test_error():
    try:
        1 / 0
    except Exception as e:
        logger.error("Intentional error triggered", exc_info=True)
        return {"error": "Intentional error triggered"}
