from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from services.shared_kernel.domain.models import Organization
from services.shared_kernel.domain.schemas import OrganizationCreate, OrganizationUpdate, OrganizationResponse
from services.shared_kernel.core.database import get_db

router = APIRouter()

@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(org_in: OrganizationCreate, db: Session = Depends(get_db)):
    db_org = Organization(**org_in.model_dump())
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

@router.get("/", response_model=List[OrganizationResponse])
def get_organizations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    orgs = db.query(Organization).offset(skip).limit(limit).all()
    return orgs

@router.get("/{org_id}", response_model=OrganizationResponse)
def get_organization(org_id: UUID, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@router.put("/{org_id}", response_model=OrganizationResponse)
def update_organization(org_id: UUID, org_in: OrganizationUpdate, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    update_data = org_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(org, key, value)
        
    db.commit()
    db.refresh(org)
    return org
