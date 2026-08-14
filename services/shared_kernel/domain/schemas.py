from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

# Users
class UserBase(BaseModel):
    email: EmailStr
    role: str = "admin"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID
    organization_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True

# Departments
class DepartmentBase(BaseModel):
    name: str
    escalation_number: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentResponse(DepartmentBase):
    id: UUID
    organization_id: UUID

    class Config:
        orm_mode = True

# VoiceConfig
class VoiceConfigBase(BaseModel):
    voice_id: Optional[str] = None
    greeting_text: Optional[str] = None
    language: str = "en"
    tone: str = "professional"

class VoiceConfigCreate(VoiceConfigBase):
    pass

class VoiceConfigResponse(VoiceConfigBase):
    id: UUID
    organization_id: UUID

    class Config:
        orm_mode = True

# BusinessRules
class BusinessRuleBase(BaseModel):
    rule_type: str
    condition: Dict[str, Any]
    action: Dict[str, Any]
    active: bool = True

class BusinessRuleCreate(BusinessRuleBase):
    pass

class BusinessRuleResponse(BusinessRuleBase):
    id: UUID
    organization_id: UUID

    class Config:
        orm_mode = True

# Organizations
class OrganizationBase(BaseModel):
    name: str
    industry_type: Optional[str] = None
    timezone: str = "UTC"
    operating_hours: Optional[Dict[str, Any]] = None
    contact_info: Optional[Dict[str, Any]] = None
    status: str = "active"

class OrganizationCreate(OrganizationBase):
    admin_email: EmailStr
    admin_password: str

class OrganizationResponse(OrganizationBase):
    id: UUID
    created_at: datetime
    departments: List[DepartmentResponse] = []
    voice_config: Optional[VoiceConfigResponse] = None
    business_rules: List[BusinessRuleResponse] = []

    class Config:
        orm_mode = True

# KnowledgeDocuments
class KnowledgeDocumentBase(BaseModel):
    source_type: str
    filename_or_url: str

class KnowledgeDocumentCreate(KnowledgeDocumentBase):
    pass

class KnowledgeDocumentResponse(KnowledgeDocumentBase):
    id: UUID
    organization_id: UUID
    status: str
    uploaded_at: datetime
    last_indexed_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# JWT
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[UUID] = None
    organization_id: Optional[UUID] = None
    role: Optional[str] = None

# Calls
class CallBase(BaseModel):
    caller_number: Optional[str] = None
    status: str = "in_progress"
    recording_url: Optional[str] = None

class CallCreate(CallBase):
    pass

class CallResponse(CallBase):
    id: UUID
    organization_id: UUID
    started_at: datetime
    ended_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# CallTurns
class CallTurnBase(BaseModel):
    turn_index: int
    speaker: str
    text: str

class CallTurnCreate(CallTurnBase):
    pass

class CallTurnResponse(CallTurnBase):
    id: UUID
    call_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True

# Escalation
class EscalationBase(BaseModel):
    department_id: Optional[UUID] = None
    reason: str
    outcome: Optional[str] = None

class EscalationCreate(EscalationBase):
    pass

class EscalationResponse(EscalationBase):
    id: UUID
    call_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True

# CollectedInfo
class CollectedInfoBase(BaseModel):
    field_name: str
    field_value: str

class CollectedInfoCreate(CollectedInfoBase):
    pass

class CollectedInfoResponse(CollectedInfoBase):
    id: UUID
    call_id: UUID

    class Config:
        orm_mode = True

# -----------------
# Ephemeral Domain Models (Not persisted directly via ORM, used by Engine)
# -----------------
class Intent(BaseModel):
    name: str
    confidence: float
    parameters: Optional[Dict[str, Any]] = None

class EscalationDecision(BaseModel):
    reason: str
    department_id: Optional[UUID] = None
    fallback_message: Optional[str] = None

