from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

# Core Domain Stubs (per Architecture.md §5 and Rules.md §1)

class Organization(BaseModel):
    id: UUID
    name: str
    industry_type: str
    timezone: str
    operating_hours: Dict[str, Any]
    contact_info: Dict[str, Any]
    status: str
    created_at: datetime

class CallTurn(BaseModel):
    id: UUID
    call_id: UUID
    turn_index: int
    speaker: str # 'caller' or 'ai'
    text: str
    created_at: datetime

class Call(BaseModel):
    id: UUID
    organization_id: UUID
    caller_number: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    status: str
    recording_url: Optional[str] = None
    turns: List[CallTurn] = []

class KnowledgeDocument(BaseModel):
    id: UUID
    organization_id: UUID
    source_type: str
    filename_or_url: str
    status: str
    uploaded_at: datetime
    last_indexed_at: Optional[datetime] = None
