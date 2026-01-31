import logging
import json
import sys
from datetime import datetime

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
        }
        
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        # Merge extra fields if any
        if hasattr(record, "extra"):
            log_record.update(record.extra)
            
        return json.dumps(log_record)

def setup_logger():
    logger = logging.getLogger("tesis_logger")
    logger.setLevel(logging.INFO)
    
    # Console Handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(JsonFormatter())
    
    # File Handler
    import os
    log_dir = "/app/logs"
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(f"{log_dir}/backend.log")
    file_handler.setFormatter(JsonFormatter())
    
    # Prevent adding multiple handlers if setup is called multiple times
    if not logger.handlers:
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)
        
    return logger

logger = setup_logger()
