from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from services.shared_kernel.domain.models import VoiceConfig
from services.shared_kernel.domain.schemas import VoiceConfigCreate, VoiceConfigResponse
from services.shared_kernel.core.database import get_db

router = APIRouter()

@router.post("/{org_id}/voice-configs", response_model=VoiceConfigResponse, status_code=status.HTTP_201_CREATED)
def create_voice_config(org_id: UUID, config_in: VoiceConfigCreate, db: Session = Depends(get_db)):
    db_config = VoiceConfig(**config_in.model_dump(), organization_id=org_id)
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

@router.get("/{org_id}/voice-configs", response_model=List[VoiceConfigResponse])
def get_voice_configs(org_id: UUID, db: Session = Depends(get_db)):
    configs = db.query(VoiceConfig).filter(VoiceConfig.organization_id == org_id).all()
    return configs

@router.put("/{org_id}/voice-configs/{config_id}", response_model=VoiceConfigResponse)
def update_voice_config(org_id: UUID, config_id: UUID, config_in: VoiceConfigCreate, db: Session = Depends(get_db)):
    config = db.query(VoiceConfig).filter(VoiceConfig.organization_id == org_id, VoiceConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Voice config not found")
    
    update_data = config_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)
        
    db.commit()
    db.refresh(config)
    return config
