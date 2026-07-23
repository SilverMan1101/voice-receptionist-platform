import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, JSON
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
