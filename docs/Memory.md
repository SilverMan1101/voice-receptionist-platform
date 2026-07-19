# Memory.md — Persistent Project Knowledge Base

> Purpose: let any future AI assistant (or new chat session) resume work on this project with minimal re-explanation. Read this file first, before `PRD.md`/`Architecture.md`/`Rules.md`/`Phases.md`/`Design.md`.

---

## 1. Project Summary

**What it is:** An enterprise, multi-tenant, organization-agnostic **AI Voice Receptionist Platform**. It answers inbound phone calls like a trained front-desk employee: greets callers, answers questions using the organization's own uploaded knowledge (RAG-grounded, zero hallucination tolerance), collects basic caller info when appropriate, and escalates to a human when needed. Every call is recorded, transcribed, and summarized; admins get analytics.

**What it explicitly is NOT:** a chatbot platform, a CRM, a call center suite, a booking/appointment system, a payment system, or a multi-agent AI system. Scope discipline on this point is a first-class project value, not a minor detail.

**Positioning analogy:** "WordPress for AI Receptionists" — one core platform, unlimited tenants, each configured purely via data/knowledge upload, never via code changes.

## 2. Key Decisions (Completed)

| Decision | Choice |
|---|---|
| Backend language/framework | Python + FastAPI |
| ORM | SQLAlchemy + Alembic |
| Primary DB | PostgreSQL |
| Cache/session store | Redis |
| Vector DB | Qdrant |
| LLM strategy | Provider-agnostic adapter layer over OpenAI / Gemini / Claude |
| STT | Adapter over Whisper or Deepgram |
| TTS | Adapter over OpenAI TTS or ElevenLabs |
| Containerization | Docker + Docker Compose |
| Reverse proxy | Nginx |
| Architecture style | Clean Architecture + DDD + SOLID, modular services in a monorepo |
| Control authority | **Conversation Engine controls the app; the LLM only reasons/generates language, never directly triggers side effects** — this is a hard architectural rule, not a preference |
| Knowledge grounding policy | No hallucinated organizational facts, ever. Below-confidence retrieval → graceful fallback + escalation, never a guess |
| Multi-tenancy | Logical isolation per tenant across DB, vector store, and object storage; zero org-specific code branches allowed |
| Branch Strategy | Trunk-based, feature branches merge directly to main via PR (no develop branch) |
| Code Review | Solo dev: PR + self-review. If team expands: 1 approval required |
| Test Coverage | CI reports coverage; no hard fail threshold yet (revisit end of Phase 2, target ~75-80%) |
| Embedding Models | Swappable adapter interface, defaults to OpenAI text-embedding-3-small |
| Confidence Scoring | MVP uses Qdrant raw vector cosine similarity score with configurable per-tenant threshold |
| Auth Service | Uses a custom JWT implementation instead of a managed provider (e.g. Auth0) for the MVP |
| Knowledge Publishing | Documents go live immediately upon successful indexing without a human-in-the-loop approval gate (Resolves OQ-7) |

## 3. Architecture Decisions

- **Pipeline shape:** Telephony → STT → Conversation Engine → (Knowledge Retrieval + Business Rules) → LLM → Response → TTS → Telephony, with async side-processes (Recording, Transcript, Summary, Analytics) fed via an Event Bus, decoupled from the live call path.
- **Statelessness:** Engine processes are stateless; per-call state lives in Redis (ephemeral), durable state lives in Postgres (persisted async).
- **Adapters everywhere:** LLM, STT, TTS, and Telephony are each behind a swappable adapter interface — this is required for organization-independence and future provider flexibility, not optional abstraction.
- **Folder structure:** documented in full in `Architecture.md` §3 — monorepo with `apps/`, `services/`, `libs/`, `infra/`, `docs/`, `tests/`.
- **Full proposed schema** (Organization, Department, KnowledgeDocument, KnowledgeChunk, BusinessRule, VoiceConfig, Call, CallTurn, CallSummary, Escalation, CollectedInfo) is in `Architecture.md` §5 — treat as the canonical starting schema.

## 4. Technology Choices — Rationale Notes

- FastAPI chosen for async-first support, essential given the streaming nature of STT/TTS/LLM I/O on the live call path.
- Qdrant: Supports production-grade scaling. Multi-tenancy enforced via payload filtering (logical isolation) rather than separate collections, ensuring simpler management for many small tenants.
- Event Bus starts as Redis Streams (MVP simplicity) with a documented graduation path to Kafka/RabbitMQ under higher throughput — not yet needed at MVP scale.

## 5. Business Rules (Core, Non-Negotiable)

1. AI never answers an organization-specific factual question without grounding it in retrieved knowledge.
2. AI always offers/executes escalation when: caller explicitly asks, information is unavailable, confidence is low, conversation exceeds configured limits, or a tenant rule mandates it.
3. AI collects only the caller data actually needed for the call's purpose — no unnecessary questions.
4. Every call gets: a recording (if tenant consents), a full transcript, and a structured summary.
5. Unanswered/low-confidence questions are logged to a per-tenant knowledge-gap queue, visible to admins.
6. No organization-specific logic in code — ever. All org differences are configuration/data.

## 6. Terminology (Canonical — use these exact terms consistently)

| Term | Meaning |
|---|---|
| **Tenant / Organization** | A business/institution using the platform (used interchangeably; prefer "Organization" in schema, "tenant" in architecture discussion) |
| **Conversation Engine** | The orchestrator that owns call control flow; the LLM is subordinate to it |
| **Knowledge Document / Knowledge Chunk** | Uploaded source document / its indexed sub-pieces for RAG |
| **Knowledge Gap** | A caller question the AI could not confidently answer, logged for admin review |
| **Escalation** | The act of transferring a call to a human, with reason and outcome tracked |
| **Business Rule** | A tenant-configured condition→action pair governing routing/escalation |
| **Call Turn** | One utterance exchange (caller or AI) within a call |
| **Containment** | A call resolved without human transfer (a nuanced success metric — over-containment can be bad if it frustrates callers) |
| **Warm transfer** | AI stays connected briefly to hand off context to the human (vs. cold transfer) |

## 7. Constraints (Carried Forward From PRD/Architecture/Rules)

- Must remain organization-agnostic at the code level.
- Must support swappable LLM/STT/TTS/Telephony providers.
- Conversation Engine must remain the sole controller of application/call flow.
- Must follow Clean Architecture / SOLID / DDD throughout.
- Recording/consent behavior must be configurable per tenant/jurisdiction.

## 8. Known Issues / Risks to Track

- No telephony provider chosen yet — blocks Phase 3 start.
- Legal/consent requirements for call recording vary by jurisdiction and are not yet researched per target region.
- Billing/pricing model for tenants is undefined.
- Brand identity (colors, typeface, logo) undefined — `Design.md` uses placeholder tokens.

## 9. Pending Decisions (See each document's "Open Questions" section for full detail)

- Telephony provider selection (`PRD.md` OQ-1, `Architecture.md` AQ-2).
- Initial language set beyond English (`PRD.md` OQ-2).
- Warm transfer requirement at MVP vs. later (`PRD.md` OQ-5).
- Kubernetes migration threshold (`Architecture.md` AQ-1).
- Secrets management tooling (`Architecture.md` AQ-4).
- Concurrent call load target for hardening phase (`Phases.md` PQ-1).
- Brand identity finalization (`Design.md` DQ-1).

## 10. Assumptions Made (Explicitly Labeled Throughout)

All assumptions are individually labeled with an ID (A1–A5 in `PRD.md`) or called out inline in `Architecture.md`/`Design.md`/`Phases.md`. The most consequential ones for any future session to be aware of:
- English-first launch, multi-language architecture supported but not required at MVP.
- Twilio-class telephony provider assumed but not selected.
- Web-based Admin Portal (React/Next.js) is the primary configuration surface.
- Docker Compose for early stages, with a Kubernetes migration path documented but not committed to a trigger point.
- Modular monolith-leaning microservice split within a single monorepo (not polyrepo).

## 11. Development Preferences (User-Stated, From Prior Sessions)

- Prefers **minimal, progressive code examples** to learn actively — avoid dumping full/complete solutions; teach step-by-step, project-based.
- In ecosystems that default to another language (e.g., Godot defaults to GDScript), prefers **C++** where feasible.
- Works on Windows 11 (ASUS TUF F15).
- Is a Computer Science Engineering student (Chandigarh University, Batch 2027) building a portfolio for placements — this project is very likely a portfolio-grade build, so documentation quality and demonstrable architecture maturity matter as much as raw feature completeness.

> **Implication for future sessions:** when writing any actual code for this project (not covered in this documentation pass), default to incremental, teaching-oriented delivery rather than handing over complete files — unless the user explicitly asks for full code.

## 12. Coding Preferences

- Documentation-first, single-source-of-truth discipline: this six-file documentation set (`PRD.md`, `Architecture.md`, `Rules.md`, `Phases.md`, `Design.md`, `Memory.md`) governs all future work and should be updated, not duplicated or contradicted, as the project evolves.
- No application code has been written yet as of this document's creation — this session's deliverable was documentation only.

## 13. Future Roadmap (Beyond Current Scope, From PRD §14)

- Appointment booking / calendar integration.
- Outbound calling.
- Multi-channel expansion (SMS/WhatsApp/web chat) reusing the Conversation Engine.
- CRM/ticketing integrations.
- Multi-agent/specialist sub-agent workflows.
- Payment collection over voice.
- Caller sentiment/emotion detection.

## 14. Important Context From Previous Discussions

- **Phase 1 Unit Testing (July 2026):** Both `tenant_config_service` and `knowledge_service` have fully functioning unit and integration test suites, with Qdrant successfully mocked in unit tests and passing real integration tests. All dependencies (like python-multipart, pytest-dotenv) are properly documented. `OPENAI_API_KEY` is sourced from `.env.local`.
- **Routing standardization:** `tenant_config_service` routes for sub-resources (departments, voice-configs, business-rules) are strictly mounted under `/api/v1/organizations/{org_id}/...`.
- The original project brief was provided as a single detailed document (v1 vision) and used as the **sole source of truth** for generating the full documentation set (`PRD.md`, `Architecture.md`, `Rules.md`, `Phases.md`, `Design.md`, `Memory.md`) in this session.
- All six documents were generated together in one pass, cross-checked for internal consistency (terminology, phase-to-architecture alignment, design-to-PRD alignment).
- Any assumption made beyond the original brief is explicitly labeled as such in the relevant document — future sessions should treat unlabeled statements as either directly sourced from the brief or a documented decision, not implicit assumptions.

## 15. How to Use This Documentation Set Going Forward

1. Start any new session by reading this `Memory.md` file.
2. Check the relevant document's **Open Questions** section before making a design decision that touches unresolved territory — resolve it with the user rather than assuming.
3. When a real decision is made (e.g., "we're using Twilio"), update: the relevant Open Question section (remove/resolve it), the Assumptions section if it replaces a prior assumption, and this `Memory.md`'s "Key Decisions" / "Pending Decisions" tables.
4. Never contradict `Rules.md` §16 ("Things That Should Never Be Done") regardless of what a later request seems to imply — surface the conflict instead.
