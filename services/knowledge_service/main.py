from fastapi import FastAPI
from services.knowledge_service.api.v1.routes import knowledge, retrieval

app = FastAPI(title="Knowledge Service", version="1.0.0")

app.include_router(knowledge.router, prefix="/api/v1", tags=["Knowledge"])
app.include_router(retrieval.router, prefix="/api/v1", tags=["Retrieval"])

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "knowledge-service"}
