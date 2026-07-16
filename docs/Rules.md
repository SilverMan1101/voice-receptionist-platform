# Rules.md — Project Constitution

> This document governs how humans and AI assistants build this project. It is binding. When in doubt, this document wins over convenience or precedent from other projects.

---

## 1. Coding Principles

1. **Clean Architecture** — dependencies point inward: `domain` knows nothing about `infrastructure`; `infrastructure` implements interfaces defined by `domain`/`application`.
2. **SOLID** — especially Single Responsibility and Dependency Inversion; provider adapters (LLM/STT/TTS/Telephony) must be swappable without touching business logic.
3. **Domain-Driven Design** — model the domain (Call, Organization, Escalation, KnowledgeDocument, BusinessRule) explicitly as first-class entities/value objects, not as raw dicts/JSON passed around.
4. **Configuration over hardcoding** — no organization-specific `if org == "X"` branches anywhere in the codebase, ever. All org differences are data.
5. **The Conversation Engine controls the application; the LLM only reasons and generates language.** Never let the LLM directly trigger side effects (DB writes, transfers, external calls) — it proposes; the Engine validates and executes via defined tools.
6. **Fail safe, not silent.** Any failure in the pipeline must degrade to a safe, honest response to the caller ("I'm having trouble right now") rather than a hallucinated answer or a dead call.
7. **No hallucination tolerance for organizational facts.** If retrieval confidence is below threshold, the AI must say so and offer escalation — never guess.

## 2. Naming Conventions

- Python: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- API routes: plural nouns, kebab-case where multi-word (`/business-rules`, not `/businessRules`).
- Database tables: `snake_case`, plural (`organizations`, `knowledge_documents`).
- Event names on the Event Bus: `domain.entity.action` (e.g., `call.escalation.triggered`, `knowledge.document.indexed`).
- Environment variables: `UPPER_SNAKE_CASE`, prefixed by service (`CONV_ENGINE_LLM_PROVIDER`).

## 3. Folder Conventions

- Follow the structure defined in `Architecture.md` §3 exactly; do not introduce ad hoc top-level folders without updating that document first.
- Each service under `services/` must contain `domain/`, `application/`, `infrastructure/`, `interfaces/` — no exceptions, even for small services.
- Shared code goes in `libs/` or `shared-kernel/` — never copy-pasted between services.

## 4. Component Rules (Admin Portal Frontend)

- Components are functional, typed, and single-responsibility.
- No business logic in UI components — components call application-layer hooks/services; validation and orchestration live outside the render tree.
- Every screen must implement loading, empty, and error states (see `Design.md`).
- Shared UI primitives live in a component library folder; no duplicate button/input implementations.

## 5. API Rules

- All endpoints versioned (`/api/v1/...`).
- All tenant-scoped endpoints must validate the authenticated principal's org membership server-side — never trust a client-supplied `organization_id` alone.
- Request/response schemas are explicitly typed (Pydantic models in FastAPI) — no free-form dicts at API boundaries.
- Breaking changes require a new API version, not an in-place change.
- All endpoints must return structured errors per `Architecture.md` §11.

## 6. Database Rules

- All schema changes go through migrations (Alembic) — never manual schema edits in any environment.
- Every table includes `id` (UUID), `created_at`, and where mutable, `updated_at`.
- Foreign keys enforce tenant scoping wherever applicable; queries must filter by `organization_id` at the repository layer as a defense-in-depth measure even when joins would technically enforce it.
- No raw SQL string interpolation — use parameterized queries/ORM only (SQL injection prevention).
- PII fields are documented and reviewed before addition; recordings/transcripts are subject to the tenant's data retention configuration.

## 7. Git Commit Conventions

Follow **Conventional Commits**:

```
<type>(<scope>): <short summary>

[optional body]
[optional footer]
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `security`.
Scope: the affected service/module (e.g., `conversation-engine`, `knowledge-service`, `admin-portal`).

Examples:
- `feat(knowledge-service): add DOCX parser to ingestion pipeline`
- `fix(conversation-engine): prevent double-escalation on timeout`

## 8. Branch Strategy

- `main` — always deployable, protected, requires PR + review.
- `develop` — integration branch (optional, if team size warrants it — see Open Questions).
- Feature branches: `feature/<scope>-<short-desc>` (e.g., `feature/knowledge-service-pdf-ingestion`).
- Fix branches: `fix/<scope>-<short-desc>`.
- No direct commits to `main`.

## 9. Documentation Rules

- Any change to system architecture must be reflected in `Architecture.md` in the same PR.
- Any change to scope (features added/removed) must update `PRD.md`'s Goals/Non-Goals sections.
- Every service must have a `README.md` covering: purpose, how to run locally, how to test, key environment variables.
- Public APIs documented via OpenAPI/Swagger, auto-generated from FastAPI where possible.

## 10. Testing Rules

- Minimum test pyramid: unit tests (domain logic, adapters mocked) > integration tests (service + real DB/Redis in test containers) > E2E tests (simulated call flow end-to-end).
- The Conversation Engine's decision logic (escalation triggers, business rules) must have unit test coverage for every rule type.
- RAG grounding behavior must be tested with adversarial cases (questions with no matching knowledge → must escalate/decline, never fabricate).
- No PR merges to `main` with failing tests or reduced coverage on core domain logic (specific % threshold TBD — see Open Questions).

## 11. Security Rules

- Never log full PII or raw call recordings to standard application logs.
- Never commit secrets, API keys, or credentials to the repository — use the secrets manager (`Architecture.md` §16).
- All external provider calls (LLM/STT/TTS/Telephony) go through the adapter layer, which is the single place API keys are referenced.
- Any new third-party integration requires a security review before being wired into the live call path.
- Cross-tenant data access is treated as a critical severity bug, not a normal bug.

## 12. Performance Rules

- No blocking synchronous I/O in the live call path — everything on the hot path (STT→Engine→Retrieval→LLM→TTS) must be async/streaming.
- Any new dependency added to the live call path must have its latency benchmarked before merging.
- Non-critical work (recording upload, summary generation, analytics) must happen asynchronously off the Event Bus, never inline in the call-handling path.

## 13. Accessibility Rules (Admin Portal)

- WCAG 2.1 AA as the baseline target.
- All interactive elements keyboard-navigable; forms have associated labels; color is never the sole means of conveying status (e.g., escalation alerts also use icon/text, not just red color).
- Sufficient color contrast per design tokens defined in `Design.md`.

## 14. Refactoring Rules

- Refactors that touch the Conversation Engine's control flow require an accompanying test-suite update proving behavior parity (or documenting the intended behavior change).
- No "big bang" rewrites of a live service — refactor behind interfaces/adapters with feature flags where risk is non-trivial.
- Dead code (unused adapters, deprecated endpoints) is deleted, not commented out.

## 15. AI Assistant Instructions

When an AI assistant (this one or a future one) works on this project, it must:

1. Treat `PRD.md`, `Architecture.md`, `Rules.md`, `Phases.md`, `Design.md`, and `Memory.md` as authoritative context — read `Memory.md` first in any new session.
2. Never introduce organization-specific logic into shared code paths.
3. Never let generated code allow the LLM to directly execute side-effecting actions; all actions go through the Conversation Engine's tool-calling boundary with validation.
4. Flag — rather than silently resolve — any contradiction it notices between these documents.
5. When information needed to proceed is missing, add/update the relevant "Open Questions" section rather than inventing an authoritative-sounding answer.
6. Prefer incremental, reviewable changes aligned with the phase currently in progress (`Phases.md`) over speculative future-proofing.
7. Update `Memory.md` with any new key decision made during a session, so future sessions don't lose that context.

## 16. Things That Should Never Be Done

- ❌ Never hardcode any organization's name, data, or logic into application code.
- ❌ Never let the AI answer a factual question about an organization without it being grounded in retrieved knowledge.
- ❌ Never let the LLM bypass the Conversation Engine to take an action directly.
- ❌ Never expand scope into chatbot/CRM/booking/payments territory without an explicit, documented PRD change.
- ❌ Never store secrets in source control.
- ❌ Never skip tenant-scoping checks on a data query, "just this once."
- ❌ Never ship call recording without respecting the tenant's consent/disclosure configuration.
- ❌ Never silently swallow a pipeline failure — always degrade to a safe response and log it.
- ❌ Never merge a change to `Architecture.md`-defined structure without updating that document.

## 17. Open Questions

- *(All Phase 0 CI/Branching questions have been resolved; see Memory.md Key Decisions).*
