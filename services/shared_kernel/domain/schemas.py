from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

# Organization Schemas

class OrganizationBase(BaseModel):
    name: str = Field(..., description="Name of the organization")
    industry_type: Optional[str] = Field(None, description="Industry type")
    timezone: str = Field("UTC", description="Operating timezone")
    operating_hours: Optional[Dict[str, Any]] = Field(None, description="Operating hours JSON")
    contact_info: Optional[Dict[str, Any]] = Field(None, description="Contact information JSON")

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(OrganizationBase):
    name: Optional[str] = None
    timezone: Optional[str] = None

class OrganizationResponse(OrganizationBase):
    id: UUID
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# User Schemas

class UserBase(BaseModel):
    email: EmailStr
    role: str = "admin"

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: UUID
    organization_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Department Schemas

class DepartmentBase(BaseModel):
    name: str
    escalation_number: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentResponse(DepartmentBase):
    id: UUID
    organization_id: UUID

    model_config = ConfigDict(from_attributes=True)

# VoiceConfig Schemas

class VoiceConfigBase(BaseModel):
    voice_id: Optional[str] = None
    greeting_text: Optional[str] = None
    language: str = "en-US"
    tone: str = "professional"

class VoiceConfigCreate(VoiceConfigBase):
    pass

class VoiceConfigResponse(VoiceConfigBase):
    id: UUID
    organization_id: UUID

    model_config = ConfigDict(from_attributes=True)

# BusinessRule Schemas

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

    model_config = ConfigDict(from_attributes=True)

# Knowledge Schemas

class KnowledgeDocumentBase(BaseModel):
    source_type: str
    filename_or_url: str

class KnowledgeDocumentResponse(KnowledgeDocumentBase):
    id: UUID
    organization_id: UUID
    status: str
    uploaded_at: datetime
    last_indexed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class KnowledgeChunkResponse(BaseModel):
    id: UUID
    document_id: UUID
    content: str
    chunk_index: int

    model_config = ConfigDict(from_attributes=True)
