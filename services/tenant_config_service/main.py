import sys
import os
from uuid import UUID
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../libs')))

from shared_kernel.core.database import get_db, engine
from shared_kernel.domain import models, schemas
from auth.jwt_validator import get_current_token_data, get_password_hash

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tenant Config Service")

# -----------------
# Organizations
# -----------------
@app.post("/api/v1/organizations", response_model=schemas.OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(org: schemas.OrganizationCreate, db: Session = Depends(get_db)):
    # Check if admin email exists
    if db.query(models.User).filter(models.User.email == org.admin_email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    db_org = models.Organization(
        name=org.name,
        industry_type=org.industry_type,
        timezone=org.timezone,
        operating_hours=org.operating_hours,
        contact_info=org.contact_info,
        status=org.status
    )
    db.add(db_org)
    db.flush() # flush to get db_org.id

    hashed_pw = get_password_hash(org.admin_password)
    db_user = models.User(
        organization_id=db_org.id,
        email=org.admin_email,
        hashed_password=hashed_pw,
        role="admin"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_org)
    return db_org

@app.get("/api/v1/organizations/me", response_model=schemas.OrganizationResponse)
def get_my_organization(
    token_data: schemas.TokenData = Depends(get_current_token_data),
    db: Session = Depends(get_db)
):
    org = db.query(models.Organization).filter(models.Organization.id == token_data.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

# -----------------
# Departments
# -----------------
@app.post("/api/v1/departments", response_model=schemas.DepartmentResponse)
def create_department(
    dept: schemas.DepartmentCreate,
    token_data: schemas.TokenData = Depends(get_current_token_data),
    db: Session = Depends(get_db)
):
    db_dept = models.Department(
        organization_id=token_data.organization_id,
        name=dept.name,
        escalation_number=dept.escalation_number
    )
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return db_dept

@app.get("/api/v1/departments", response_model=List[schemas.DepartmentResponse])
def list_departments(
    token_data: schemas.TokenData = Depends(get_current_token_data),
    db: Session = Depends(get_db)
):
    return db.query(models.Department).filter(models.Department.organization_id == token_data.organization_id).all()

# -----------------
# Business Rules
# -----------------
@app.post("/api/v1/business-rules", response_model=schemas.BusinessRuleResponse)
def create_business_rule(
    rule: schemas.BusinessRuleCreate,
    token_data: schemas.TokenData = Depends(get_current_token_data),
    db: Session = Depends(get_db)
):
    db_rule = models.BusinessRule(
        organization_id=token_data.organization_id,
        rule_type=rule.rule_type,
        condition=rule.condition,
        action=rule.action,
        active=rule.active
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

@app.get("/api/v1/business-rules", response_model=List[schemas.BusinessRuleResponse])
def list_business_rules(
    token_data: schemas.TokenData = Depends(get_current_token_data),
    db: Session = Depends(get_db)
):
    return db.query(models.BusinessRule).filter(models.BusinessRule.organization_id == token_data.organization_id).all()

# -----------------
# Voice Config
# -----------------
@app.put("/api/v1/voice-config", response_model=schemas.VoiceConfigResponse)
def update_voice_config(
    config: schemas.VoiceConfigCreate,
    token_data: schemas.TokenData = Depends(get_current_token_data),
    db: Session = Depends(get_db)
):
    db_config = db.query(models.VoiceConfig).filter(models.VoiceConfig.organization_id == token_data.organization_id).first()
    if db_config:
        db_config.voice_id = config.voice_id
        db_config.greeting_text = config.greeting_text
        db_config.language = config.language
        db_config.tone = config.tone
    else:
        db_config = models.VoiceConfig(
            organization_id=token_data.organization_id,
            voice_id=config.voice_id,
            greeting_text=config.greeting_text,
            language=config.language,
            tone=config.tone
        )
        db.add(db_config)
    
    db.commit()
    db.refresh(db_config)
    return db_config

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "tenant_config_service"}
