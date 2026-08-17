# Enterprise AI Voice Receptionist Platform

An enterprise-grade, multi-tenant AI voice receptionist system. It answers incoming phone calls on behalf of businesses, greets callers naturally, answers questions using the organization's approved knowledge base (RAG), collects caller information, and escalates to human staff when appropriate.

It is explicitly **not** a chatbot, CRM, or generic AI agent platform. It is a strictly controlled voice reception system designed around a "WordPress for AI Receptionists" model: one core engine, infinite tenants, configured entirely via data and UI, with zero organization-specific code.

## Key Features

- **Multi-Tenant Architecture:** Strict logical isolation between organizations using payload filtering and RBAC. Zero code changes required to onboard a new organization.
- **Strict Knowledge Grounding (RAG):** Answers are generated *only* from approved uploaded documents (PDF, Markdown, TXT). If the AI is not confident, it falls back and escalates. Zero hallucination tolerance.
- **Conversation Engine Authority:** The LLM does not control the call. A deterministic Conversation Engine manages state, limits, and executes side-effects (like knowledge retrieval or escalation) based on strict LLM tool-calling boundaries.
- **Admin Configuration Portal:** A full Next.js dashboard for non-technical admins to upload knowledge, configure operating hours, set up routing departments, and review call history/analytics.
- **Provider Agnostic:** Built with adapter layers for Telephony (Twilio), Speech-to-Text (Gemini/Deepgram), Text-to-Speech (Gemini/ElevenLabs), and LLM reasoning (Gemini/OpenAI).

## Technology Stack

### Backend & Infrastructure
- **Language/Framework:** Python 3.12, FastAPI
- **Primary Database:** PostgreSQL (SQLAlchemy + Alembic)
- **Vector Database:** Qdrant (for RAG)
- **State & Caching:** Redis (Ephemeral call state, rate limiting)
- **Containerization:** Docker & Docker Compose

### Frontend (Admin Portal)
- **Framework:** Next.js 14, React 18
- **Styling:** Tailwind CSS
- **Auth:** Custom JWT Authentication (tenant-scoped)

## Repository Structure

```text
voice-receptionist-platform/
├── apps/
│   ├── admin_portal/          # Next.js Frontend Dashboard
│   └── voice_runtime/         # Real-time telephony webhook and audio stream handler
├── services/
│   ├── auth_service/          # JWT authentication and user management
│   ├── conversation_engine/   # Core turn processing, tool routing, and orchestration
│   ├── knowledge_service/     # Document parsing, embedding, and vector search
│   ├── tenant_config_service/ # CRUD APIs for organization rules, hours, and config
│   └── shared_kernel/         # Shared domain models (SQLAlchemy), schemas, and DB setup
├── libs/
│   ├── auth/                  # JWT validation helpers
│   ├── llm_adapters/          # OpenAI / Gemini / Claude implementations
│   ├── embedding_adapters/    # Vector embedding implementations
│   ├── document_parsers/      # LangChain PDF/text loaders
│   └── telephony_adapters/    # Twilio API wrappers
├── infra/                     # Docker compose and environment configurations
└── docs/                      # Comprehensive architectural and product documentation
```

## Local Development Setup

### Prerequisites
- Python 3.12
- Node.js 18+
- Docker and Docker Compose
- A Twilio Account (for telephony integration)
- API Keys for Gemini and/or OpenAI

### 0. VENV Setup
first install python 3.12 only:
```bash
python -m venv venv
pip install -r requirements.txt
```


### 1. Start Infrastructure
Run the core databases (Postgres, Redis, Qdrant) and the backend API services (Auth, Knowledge, Tenant Config):
```bash
cd infra
docker-compose up -d
```
*(This starts services on ports `5432`, `6379`, `6333`, `8001`, `8002`, `8003`)*

### 2. Run the Conversation Engine (Standalone)
The core engine runs outside of docker-compose in development:
```bash
source venv/Scripts/activate  # Or venv/bin/activate on Mac/Linux
uvicorn services.conversation_engine.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Run the Voice Runtime  (Standalone)
The core engine runs outside of docker-compose in development:
```bash
source venv/Scripts/activate  # Or venv/bin/activate on Mac/Linux
uvicorn apps.voice_runtime.main:app --host 127.0.0.1 --port 8004 --reload
```

### 4. Run the Voice Runtime localhost on ngrok (Standalone)
The core engine runs outside of docker-compose in development:
install ngrok through Microsoft Store
```bash
ngrok http 8004
```

### 5. Run the Admin Portal (Frontend)
```bash
cd apps/admin_portal
npm install
npm run dev
```
Access the dashboard at `http://localhost:3000`.

## Documentation

This project enforces a strict documentation-driven development process. Please read the full documentation set located in the `docs/` directory before making architectural changes:

1. `Memory.md` — Persistent Project Knowledge Base (Read this first)
2. `PRD.md` — Product Requirements and Scope Limits
3. `Architecture.md` — System Design, Schema, and Interfaces
4. `Rules.md` — Project Constitution (Binding rules on logic and isolation)
5. `Phases.md` — Implementation Roadmap
6. `Design.md` — Admin Portal UX/UI Spec

## License
Copyright © Enterprise AI Voice Receptionist Platform. All rights reserved.
