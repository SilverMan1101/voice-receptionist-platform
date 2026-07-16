# PRD.md — Enterprise AI Voice Receptionist Platform

> **Status:** Draft v1.0
> **Document owner:** Product/Architecture (AI-assisted)
> **Companion documents:** `Architecture.md`, `Rules.md`, `Phases.md`, `Design.md`, `Memory.md`

---

## 1. Project Overview

The Enterprise AI Voice Receptionist Platform ("the Platform") is a **multi-tenant, organization-agnostic system** that answers incoming phone calls on behalf of any business and performs the duties of a trained front-desk receptionist: greeting callers, answering questions from the organization's own knowledge base, collecting basic caller information, and escalating to a human when appropriate.

It is explicitly **not** a chatbot, CRM, call center suite, or appointment-booking system. It is a single-purpose, deeply-executed **voice reception** product — think "WordPress for AI Receptionists": one core engine, infinite tenants, each configured purely through data (documents, business rules, voice settings) rather than code.

## 2. Vision

> Any organization — from a two-doctor clinic to a multi-branch bank — should be able to sign up, upload its knowledge, configure its business hours and escalation rules, connect a phone number, and within an hour have an AI receptionist that sounds professional, knows the organization's information cold, and never pretends to know what it doesn't.

## 3. Problem Statement

* Human receptionists are expensive, unavailable 24/7, and inconsistent across shifts.
* Small and mid-size organizations cannot justify a full-time front-desk hire but still lose business to unanswered calls.
* Existing voice-bot tools are either narrow single-purpose IVRs (rigid menu trees, poor comprehension) or general-purpose chatbot platforms retrofitted for voice (not receptionist-shaped, prone to hallucination, no telephony-grade conversation control).
* Organizations need a system that **never invents facts** about them, that escalates gracefully instead of frustrating the caller, and that can be reconfigured by non-technical staff by simply uploading documents.

## 4. Goals

| # | Goal |
|---|------|
| G1 | Handle inbound phone calls with natural, low-latency, human-like conversation. |
| G2 | Answer only from organization-approved knowledge (RAG), with zero tolerance for hallucinated business facts. |
| G3 | Be fully organization-independent — zero organization-specific logic in the codebase. |
| G4 | Escalate to a human cleanly and contextually when the AI cannot help. |
| G5 | Record, transcribe, and summarize every call for admin visibility. |
| G6 | Provide analytics that let admins improve the knowledge base and operations over time. |
| G7 | Be operable by non-technical org admins via a configuration/knowledge portal — no code changes per tenant. |

## 5. Non-Goals

* Not building a general chatbot or website chat widget (may reuse the Conversation Engine later, but out of scope now).
* Not building a CRM, ticketing system, or sales pipeline.
* Not building outbound/proactive calling (this phase is inbound-only).
* Not building payment processing.
* Not building appointment scheduling/booking logic (may consume an external calendar in the future, but no booking engine is built).
* Not building a multi-agent autonomous AI system — one bounded Conversation Engine, one role: receptionist.

## 6. Target Users

1. **Organization Admin** — configures the receptionist for their org (uploads docs, sets hours, escalation numbers, voice).
2. **Front-desk / Escalation Staff** — receive transferred calls and read call summaries.
3. **Business Owner / Decision Maker** — reviews analytics, ROI, call volume trends.
4. **Caller (external, unauthenticated)** — the person phoning in; not a platform user but the primary conversational counterpart.
5. **Platform Operator (Anthropic-style SaaS admin)** — Anthropic-of-this-platform staff who manage tenants, billing, uptime, and abuse.

## 7. User Personas

### 7.1 Priya — Clinic Administrator
Runs a 3-doctor clinic. Not technical. Wants callers to get accurate answers about hours, insurance accepted, and directions, and to be transferred to the front desk for anything involving a specific patient. Success = fewer missed calls, no wrong medical claims made by the AI.

### 7.2 Daniel — Hotel Operations Manager
Manages a boutique hotel. Wants the AI to answer FAQs (check-in time, pet policy, amenities) and immediately transfer booking/payment calls to a human. Cares about call recordings for dispute resolution.

### 7.3 Meera — University Admissions Officer
Wants the AI to handle high call volume during admission season (deadlines, fee structure, program info), collect prospective-student contact details, and escalate complex eligibility questions.

### 7.4 Alex — Platform Operator
Manages the SaaS platform itself: onboarding new tenants, monitoring uptime, telephony costs, and abuse/misuse detection across all tenants.

## 8. User Stories

| ID | As a... | I want to... | So that... |
|----|---------|---------------|------------|
| US-1 | Org Admin | upload PDFs/DOCX/FAQ sheets | the AI answers using our real information |
| US-2 | Org Admin | configure business hours, departments, and escalation numbers | calls route correctly |
| US-3 | Caller | ask a question in natural speech | I get an accurate spoken answer without navigating a menu |
| US-4 | Caller | ask to speak to a human | I'm transferred promptly and politely |
| US-5 | Org Admin | see a summary and transcript after each call | I don't have to listen to the whole recording |
| US-6 | Org Admin | see which questions the AI couldn't answer | I know what to add to the knowledge base |
| US-7 | Business Owner | view call volume and transfer-rate analytics | I can measure ROI and staffing needs |
| US-8 | Org Admin | set the AI's voice, greeting, and tone | it matches our brand |
| US-9 | Platform Operator | onboard a new organization without writing code | the platform scales across tenants |
| US-10 | Caller | have my basic details collected naturally | I don't have to repeat myself when transferred |

## 9. Functional Requirements

### 9.1 Voice & Conversation
- FR-1: System answers inbound calls via a telephony provider integration.
- FR-2: System performs streaming speech-to-text with low latency, multi-language support, and noise tolerance.
- FR-3: The Conversation Engine maintains per-call state and context across turns.
- FR-4: The Conversation Engine — not the LLM — decides next actions, tool invocation, and escalation; the LLM is only invoked for reasoning/language generation within engine-defined bounds.
- FR-5: System supports barge-in / interruption handling.
- FR-6: System converts responses to speech via TTS and streams audio back to the caller.

### 9.2 Knowledge & Retrieval
- FR-7: Org Admins can upload PDF, DOCX, TXT, Markdown, CSV, XLSX, JSON, and website URLs as knowledge sources.
- FR-8: Uploaded content is chunked, embedded, and indexed into a per-tenant vector namespace.
- FR-9: All factual answers about the organization must be grounded in retrieved knowledge; the system must refuse or escalate rather than fabricate when confidence is low.
- FR-10: Admins can edit/delete/re-index individual knowledge documents.

### 9.3 Caller Data Collection
- FR-11: The AI may collect name, phone, email, organization, city, and reason-for-call when contextually appropriate.
- FR-12: Collected data is validated (e.g., phone/email format) and attached to the call record.
- FR-13: The AI must not ask for information not needed for the current call purpose.

### 9.4 Escalation
- FR-14: The AI transfers to a human when: caller explicitly requests it, required info is unavailable, model confidence is below threshold, conversation exceeds configured turn/time limits, or a tenant business rule mandates it.
- FR-15: Before transfer, the AI apologizes/informs the caller and passes a structured summary to the receiving human/system (via warm transfer metadata or a follow-up notification if warm transfer is unavailable).
- FR-16: Escalation events, reasons, and outcomes are logged.

### 9.5 Recording, Summaries, Logging
- FR-17: Every call is recorded (audio) and transcribed, subject to tenant configuration and legal consent requirements.
- FR-18: A structured summary is generated per call: purpose, questions asked, answers given, data collected, escalation status.
- FR-19: Unanswered/low-confidence questions are logged to a per-tenant "knowledge gaps" queue for admin review.

### 9.6 Analytics
- FR-20: Dashboard shows call volume, average duration, average response latency, top FAQs, transfer rate, unanswered-question rate, daily/weekly trends.

### 9.7 Multi-Tenancy & Configuration
- FR-21: All organization-specific data (name, services, FAQs, policies, hours, contacts, departments, documents, voice config) is stored as configuration, never as code.
- FR-22: Onboarding a new organization requires no code deployment — only configuration and knowledge upload through the admin portal / API.
- FR-23: Tenant data (knowledge, recordings, transcripts, analytics) is logically isolated per organization.

## 10. Non-Functional Requirements

| Category | Requirement |
|---|---|
| Latency | End-to-end response latency (caller stops speaking → AI starts speaking) should target < 1.5s p50 / < 3s p95 (Assumption — see Open Questions). |
| Availability | 99.9% uptime target for the call-handling path (Assumption). |
| Scalability | Must support many tenants and concurrent calls per tenant without cross-tenant interference; horizontally scalable stateless services. |
| Security | Encryption in transit and at rest; tenant data isolation; least-privilege access; PII handling compliant with applicable regulations. |
| Compliance | Call recording must respect consent laws (varies by jurisdiction) — configurable per-tenant recording disclosure. |
| Accuracy | No hallucinated organizational facts; grounded answers only, with graceful "I don't know, let me connect you" fallback. |
| Maintainability | Clean Architecture, SOLID, DDD — supports long-term extension without rewrites. |
| Observability | Full tracing of each call's pipeline stages for debugging and QA. |
| Localization | Multi-language STT/TTS support (initial language set TBD — see Open Questions). |
| Cost efficiency | Vector search, LLM, and telephony costs must be monitorable per tenant for billing/margin visibility. |

## 11. Success Metrics

- Call answer rate (calls successfully handled vs. dropped/failed).
- Containment rate (% of calls resolved without human transfer) vs. appropriate escalation rate (should not be conflated — over-containment that frustrates callers is a failure mode).
- Caller satisfaction (post-call survey / sentiment, future phase).
- Knowledge-gap closure rate (how quickly admins fill logged gaps).
- Average handle time vs. human receptionist baseline.
- Tenant onboarding time (target: knowledge upload to live receptionist in < 1 hour).

## 12. Constraints

- Must remain organization-agnostic at the code level — no vertical-specific hardcoding.
- Must support swappable LLM/STT/TTS providers via adapters (OpenAI / Gemini / Claude; Whisper/Deepgram; OpenAI TTS/ElevenLabs).
- Must use the defined technology stack (see `Architecture.md`) unless a documented decision changes it.
- The Conversation Engine, not the LLM, must remain the authority over application control flow (safety/architecture constraint, not just a preference).

## 13. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Hallucinated business facts (e.g., wrong pricing, wrong medical/legal info) | High — trust, liability | Strict RAG grounding, confidence thresholds, escalation-on-uncertainty, no-answer-without-source policy |
| STT/TTS latency causing unnatural pauses | Medium — user experience | Streaming pipelines, provider benchmarking, caching common TTS phrases |
| Telephony provider outage | High — full service outage | Provider abstraction layer, secondary provider fallback (future phase) |
| Regulatory/consent issues with call recording | High — legal | Per-tenant, per-jurisdiction consent configuration; recording disclosure announcement |
| Multi-tenant data leakage | Critical — security/trust | Strict tenant-scoped data access, per-tenant vector namespaces, automated isolation tests |
| Over-broad scope creep (becoming a chatbot/CRM) | Medium — product focus | Explicit Non-Goals enforced in `Rules.md` |
| Cost overrun from LLM/telephony usage at scale | Medium — margin | Per-tenant usage metering and budgets |

## 14. Future Features (explicitly out of current scope)

- Appointment booking / calendar integration.
- Outbound calling (reminders, confirmations).
- Multi-channel (SMS/WhatsApp/web chat) — reusing the Conversation Engine.
- CRM/ticketing integrations.
- Multi-agent workflows (e.g., specialist sub-agents per department).
- Payment collection over voice.
- Advanced caller sentiment/emotion detection.

## 15. Assumptions

*(Explicitly labeled — not sourced from the original brief.)*

- **A1:** Initial launch targets English with architecture supporting additional languages later.
- **A2:** Telephony integration will use a provider offering SIP/PSTN-to-API bridging (e.g., Twilio-class provider) — specific provider not yet chosen.
- **A3:** Tenants are billed on a usage basis (call minutes, storage) — billing model not yet designed in detail.
- **A4:** "Warm transfer" (AI stays on the line briefly to hand off context) is preferred over "cold transfer," where feasible with the chosen telephony provider.
- **A5:** A web-based Admin Portal is the primary configuration surface (vs. API-only) for non-technical admins.

## 16. Open Questions

- OQ-1: Which telephony provider(s) will be integrated first (Twilio, Vonage, Plivo, SIP trunk direct)?
- OQ-2: What is the target initial language set beyond English?
- OQ-3: What are the exact legal/consent requirements per target region (US, EU, India, etc.) for call recording?
- OQ-4: What is the pricing/billing model for tenants (per-minute, per-seat, flat SaaS tiers)?
- OQ-5: Is warm transfer technically required at launch, or is a "please hold, we'll call you back" pattern acceptable for MVP?
- OQ-6: What confidence-scoring mechanism will be used to decide "escalate due to low confidence" (numeric threshold from retrieval score, LLM self-reported confidence, or a dedicated classifier)?
- OQ-7: Should there be a human-in-the-loop approval step for newly uploaded knowledge before it goes live?
