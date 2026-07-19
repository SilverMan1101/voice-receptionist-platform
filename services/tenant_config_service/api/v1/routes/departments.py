from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from services.shared_kernel.domain.models import Department
from services.shared_kernel.domain.schemas import DepartmentCreate, DepartmentResponse, DepartmentBase
from services.shared_kernel.core.database import get_db

router = APIRouter()

@router.post("/{org_id}/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(org_id: UUID, dept_in: DepartmentCreate, db: Session = Depends(get_db)):
    db_dept = Department(**dept_in.model_dump(), organization_id=org_id)
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return db_dept

@router.get("/{org_id}/departments", response_model=List[DepartmentResponse])
def get_departments(org_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    depts = db.query(Department).filter(Department.organization_id == org_id).offset(skip).limit(limit).all()
    return depts

@router.delete("/{org_id}/departments/{dept_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(org_id: UUID, dept_id: UUID, db: Session = Depends(get_db)):
    dept = db.query(Department).filter(Department.organization_id == org_id, Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    
    db.delete(dept)
    db.commit()
    return None
