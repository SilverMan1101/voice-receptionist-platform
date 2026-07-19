from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, JSON, DateTime, func
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    industry_type = Column(String(100), nullable=True)
    timezone = Column(String(50), default="UTC")
    operating_hours = Column(JSON, nullable=True)
    contact_info = Column(JSON, nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    departments = relationship("Department", back_populates="organization", cascade="all, delete-orphan")
    voice_configs = relationship("VoiceConfig", back_populates="organization", cascade="all, delete-orphan")
    business_rules = relationship("BusinessRule", back_populates="organization", cascade="all, delete-orphan")
    knowledge_documents = relationship("KnowledgeDocument", back_populates="organization", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="admin") # e.g. platform_operator, owner, admin, staff, analyst
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="users")

class Department(Base):
    __tablename__ = "departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    escalation_number = Column(String(50), nullable=True)

    organization = relationship("Organization", back_populates="departments")

class VoiceConfig(Base):
    __tablename__ = "voice_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    voice_id = Column(String(100), nullable=True)
    greeting_text = Column(Text, nullable=True)
    language = Column(String(50), default="en-US")
    tone = Column(String(50), default="professional")

    organization = relationship("Organization", back_populates="voice_configs")

class BusinessRule(Base):
    __tablename__ = "business_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    rule_type = Column(String(100), nullable=False) # e.g. escalation, routing, data_collection
    condition = Column(JSON, nullable=False)
    action = Column(JSON, nullable=False)
    active = Column(Boolean, default=True)

    organization = relationship("Organization", back_populates="business_rules")

class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    source_type = Column(String(50), nullable=False) # e.g. pdf, url, text
    filename_or_url = Column(String(500), nullable=False)
    status = Column(String(50), default="pending") # pending, indexing, indexed, failed
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    last_indexed_at = Column(DateTime(timezone=True), nullable=True)

    organization = relationship("Organization", back_populates="knowledge_documents")
    chunks = relationship("KnowledgeChunk", back_populates="document", cascade="all, delete-orphan")

class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_documents.id"), nullable=False)
    content = Column(Text, nullable=False)
    vector_ref = Column(String(255), nullable=True) # ID mapping to Qdrant payload/vector
    chunk_index = Column(Integer, nullable=False)

    document = relationship("KnowledgeDocument", back_populates="chunks")
