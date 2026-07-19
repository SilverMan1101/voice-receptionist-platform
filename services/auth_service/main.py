from fastapi import FastAPI
from api.v1.routes import auth

app = FastAPI(title="Auth Service", version="1.0.0")

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "auth-service"}
