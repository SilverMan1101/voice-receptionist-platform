import logging
from fastapi import FastAPI, Request
import json
import time

# Structured JSON logging setup
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "service": "conversation-engine", # Change this per service
            "level": record.levelname,
            "message": record.getMessage(),
            "name": record.name
        }
        # Include trace_id, org_id, call_id if they exist in record.args or kwargs (custom logic can be added)
        if hasattr(record, "trace_id"):
            log_record["trace_id"] = record.trace_id
        return json.dumps(log_record)

logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(JSONFormatter())
if not logger.handlers:
    logger.addHandler(ch)

# OpenTelemetry placeholder (no-op for now)
def setup_opentelemetry(app: FastAPI):
    # TODO: Wire up OpenTelemetry instrumentor here
    pass

app = FastAPI(title="Voice Receptionist Platform Base Service")
setup_opentelemetry(app)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info("Request processed", extra={"method": request.method, "url": str(request.url), "process_time": process_time})
    return response

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "conversation-engine"}
