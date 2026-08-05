import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    industry_type = Column(String, nullable=True)
    timezone = Column(String, default="UTC")
    operating_hours = Column(JSON, nullable=True)
    contact_info = Column(JSON, nullable=True)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    departments = relationship("Department", back_populates="organization", cascade="all, delete-orphan")
    knowledge_documents = relationship("KnowledgeDocument", back_populates="organization", cascade="all, delete-orphan")
    business_rules = relationship("BusinessRule", back_populates="organization", cascade="all, delete-orphan")
    voice_config = relationship("VoiceConfig", uselist=False, back_populates="organization", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="admin")  # "platform_operator", "admin", "staff"
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")

class Department(Base):
    __tablename__ = "departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)
    escalation_number = Column(String, nullable=True)

    organization = relationship("Organization", back_populates="departments")

class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    source_type = Column(String, nullable=False) # e.g., 'pdf', 'url', 'text'
    filename_or_url = Column(String, nullable=False)
    status = Column(String, default="pending") # "pending", "indexed", "failed"
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    last_indexed_at = Column(DateTime, nullable=True)

    organization = relationship("Organization", back_populates="knowledge_documents")

class BusinessRule(Base):
    __tablename__ = "business_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    rule_type = Column(String, nullable=False) # e.g., 'escalation', 'routing'
    condition = Column(JSON, nullable=False)
    action = Column(JSON, nullable=False)
    active = Column(Boolean, default=True)

    organization = relationship("Organization", back_populates="business_rules")

class VoiceConfig(Base):
    __tablename__ = "voice_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, unique=True)
    voice_id = Column(String, nullable=True)
    greeting_text = Column(String, nullable=True)
    language = Column(String, default="en")
    tone = Column(String, default="professional")

    organization = relationship("Organization", back_populates="voice_config")

class Call(Base):
    __tablename__ = "calls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    caller_number = Column(String, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    status = Column(String, default="in_progress")
    recording_url = Column(String, nullable=True)

    turns = relationship("CallTurn", back_populates="call", cascade="all, delete-orphan")
    escalation = relationship("Escalation", uselist=False, back_populates="call", cascade="all, delete-orphan")
    collected_info = relationship("CollectedInfo", back_populates="call", cascade="all, delete-orphan")

class CallTurn(Base):
    __tablename__ = "call_turns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id"), nullable=False)
    turn_index = Column(Integer, nullable=False)
    speaker = Column(String, nullable=False) # "caller" or "ai"
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    call = relationship("Call", back_populates="turns")

class Escalation(Base):
    __tablename__ = "escalations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id"), nullable=False, unique=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    reason = Column(String, nullable=False)
    outcome = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    call = relationship("Call", back_populates="escalation")
    department = relationship("Department")

class CollectedInfo(Base):
    __tablename__ = "collected_info"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id"), nullable=False)
    field_name = Column(String, nullable=False)
    field_value = Column(String, nullable=False)

    call = relationship("Call", back_populates="collected_info")

