from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from services.shared_kernel.domain.models import BusinessRule
from services.shared_kernel.domain.schemas import BusinessRuleCreate, BusinessRuleResponse
from services.shared_kernel.core.database import get_db

router = APIRouter()

@router.post("/{org_id}/business-rules", response_model=BusinessRuleResponse, status_code=status.HTTP_201_CREATED)
def create_business_rule(org_id: UUID, rule_in: BusinessRuleCreate, db: Session = Depends(get_db)):
    db_rule = BusinessRule(**rule_in.model_dump(), organization_id=org_id)
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

@router.get("/{org_id}/business-rules", response_model=List[BusinessRuleResponse])
def get_business_rules(org_id: UUID, db: Session = Depends(get_db)):
    rules = db.query(BusinessRule).filter(BusinessRule.organization_id == org_id).all()
    return rules

@router.delete("/{org_id}/business-rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_business_rule(org_id: UUID, rule_id: UUID, db: Session = Depends(get_db)):
    rule = db.query(BusinessRule).filter(BusinessRule.organization_id == org_id, BusinessRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Business rule not found")
    
    db.delete(rule)
    db.commit()
    return None
