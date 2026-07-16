# AGENTS.md

This project has a full documentation set in `/docs`. **Read these before any task**, in this order:

1. `docs/Memory.md` — project summary, key decisions, terminology, current open questions
2. `docs/PRD.md` — requirements, scope, goals/non-goals
3. `docs/Architecture.md` — technical design, stack, schema, folder structure
4. `docs/Rules.md` — binding coding/process rules (treat as project constitution)
5. `docs/Phases.md` — the only valid build order; do not skip ahead
6. `docs/Design.md` — Admin Portal UX/design spec

## Hard rules (non-negotiable, duplicated here for visibility)

- Never hardcode organization-specific logic anywhere in the codebase. All org differences are configuration/data.
- The Conversation Engine controls the application. The LLM only reasons and generates language — it must never trigger a side effect directly; it proposes tool calls, the Engine validates and executes them.
- Never let the AI answer an organization-specific factual question without grounding it in retrieved knowledge (RAG). No answer without a source, ever.
- Follow the phase order in `docs/Phases.md`. Do not build voice/telephony (Phase 3) before the Conversation Engine is validated in text mode (Phase 2).
- Follow the folder structure defined in `docs/Architecture.md` §3 exactly.
- If something needed to proceed isn't decided yet, check `docs/Memory.md` §9 "Pending Decisions" and the relevant doc's "Open Questions" — ask the user, don't invent an answer.
- Any change to scope, architecture, or phase plan must be reflected back into the relevant doc in `/docs` in the same change.

## Working agreement

- Use Planning Mode for anything beyond a trivial fix — this project is deliberately staged, and skipping the plan risks building ahead of the current phase.
- Work one phase, one milestone at a time. Confirm a milestone is done (per its Acceptance Criteria in `docs/Phases.md`) before moving to the next.
- After completing meaningful work, propose an update to `docs/Memory.md` (new decisions made, questions resolved) rather than leaving that context only in chat history.

## Git workflow

- Never commit or push directly to `main`. `main` is protected per `docs/Rules.md` §8.
- Before starting any phase or milestone, create/switch to a branch named
  `feature/<phase-or-scope>-<short-desc>`, e.g. `feature/phase0-scaffolding`,
  `feature/knowledge-service-pdf-ingestion`. One branch per phase or milestone,
  not one branch for the whole project.
- Commit in small, reviewable chunks — not one giant commit per phase. Each
  commit should represent one coherent change (one milestone task, roughly).
- Use Conventional Commits per `docs/Rules.md` §7:
  `<type>(<scope>): <short summary>`, types: `feat`, `fix`, `refactor`, `docs`,
  `test`, `chore`, `perf`, `security`. Scope = the affected service/module
  (e.g. `conversation-engine`, `knowledge-service`, `admin-portal`).
- Never run `git push`, `git push --force`, or any command that rewrites
  shared history without explicit approval in that turn — ask first.
- Never merge a feature branch into `main` yourself — prepare it, summarize
  the diff, and let the user merge (or explicitly approve the merge).
- If a task is abandoned or goes wrong, prefer `git checkout -- .` /
  `git reset --hard HEAD` on the feature branch over trying to manually
  undo changes file-by-file.
