from fastapi import FastAPI
from services.tenant_config_service.api.v1.routes import organizations, departments, voice_configs, business_rules

app = FastAPI(title="Tenant Config Service", version="1.0.0")

app.include_router(organizations.router, prefix="/api/v1/organizations", tags=["Organizations"])
app.include_router(departments.router, prefix="/api/v1/organizations", tags=["Departments"])
app.include_router(voice_configs.router, prefix="/api/v1/organizations", tags=["Voice Configs"])
app.include_router(business_rules.router, prefix="/api/v1/organizations", tags=["Business Rules"])

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "tenant-config-service"}
