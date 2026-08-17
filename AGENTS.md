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

## Naming & folder discipline

- Python packages/directories under `services/`, `libs/`, and `tests/` use
  `snake_case` (e.g. `knowledge_service`, `tenant_config_service`,
  `document_parsers`) — this is a deliberate, documented exception to the
  general kebab-case convention, required because Python cannot import a
  package name containing a hyphen. This is recorded in `docs/Rules.md` §2 —
  do not deviate from it in either direction.
- Before creating ANY new folder under `services/` or `libs/`, first check
  whether a folder for that same service/module already exists under a
  different name or casing (e.g. `knowledge-service` vs `knowledge_service`,
  `conversation-engine` vs `conversation_engine`). Search the existing tree
  — do not assume based on `docs/Architecture.md` §3 alone, since that
  document can lag behind what's actually in the repo.
- If you find that a naming inconsistency already exists (two folders for
  what should be one service/module), do not build alongside it or work
  around it — stop, consolidate into the single correct `snake_case` name,
  delete the incorrect duplicate entirely, and confirm no code still
  references the deleted path (imports, docker-compose, CI config) before
  continuing with the original task.
- Every folder name actually present in the repo under `services/` and
  `libs/` must have a matching entry in `docs/Architecture.md` §3 using the
  identical name and casing — if you create a folder that isn't yet listed
  there, add it to §3 in the same change, don't leave the doc to drift.
- The same rule applies to service names used elsewhere for consistency:
  docker-compose service keys, container names, import paths, and
  `docs/Architecture.md` should all refer to the same service using
  matching names — a service should never be `knowledge-service` in
  docker-compose but `knowledge_service` as a Python import path without
  that being an intentional, documented exception (as above), not an
  accidental drift.

## Environment discipline

- This project uses one virtual environment at `venv/` in the project root.
  Never install any Python package globally / system-wide, for any reason.
- Before running ANY `pip`, `python`, `pytest`, or `uvicorn` command in a
  terminal, first confirm the venv is active — the prompt should show
  `(venv)`. If it doesn't, activate it first:
  `.\venv\Scripts\Activate.ps1` (PowerShell) — do not proceed until it's active.
- If a new terminal, worktree, or task session is started, treat the venv as
  NOT active by default. Re-activate it explicitly at the start of that
  session before running any Python command — never assume a previous
  session's state carries over.
- Prefer being fully explicit over relying on an activated shell state:
  `.\venv\Scripts\python.exe -m pip install -r requirements.txt` and
  `.\venv\Scripts\python.exe -m pytest` work correctly regardless of whether
  activation happened, and are the safer default when in doubt.
- If you ever detect that a package was installed outside `venv/` (e.g. `pip
  list` run outside the venv shows project dependencies), stop and flag it
  to the user rather than continuing — don't silently keep working around it.
- Every new dependency must be added to `requirements.txt` in the same
  change that introduces it — never left as an ad hoc local install.

## Definition of done for UI / frontend work

This exists because a prior Phase 5 attempt was marked complete in
task.md while multiple screens were literally placeholder text ("X form
will go here") instead of real implementation, there was no login page
at all despite auth_service being real, and a Dashboard showed fake
numbers with zero disclosure — none of which was caught until the user
opened a browser and checked by hand. That must never happen again.

- A screen or component is NOT "built" or "[x]" if it contains any
  placeholder text describing what it will do instead of the real
  implementation (e.g. "X form will go here", "Connects to Y service" as
  literal rendered text). Every checked-off UI deliverable must be the
  real, working thing — wired to the real backend API it's supposed to
  call — not a stub, regardless of how minor it seems.
- If a genuine reason exists to defer part of a UI deliverable (e.g. a
  real upstream dependency doesn't exist yet, like Phase 4's recording
  data during Phase 5), that specific piece must be handled exactly like
  the approved mock/real data boundary pattern: an obviously-labeled,
  clearly-disabled placeholder the user cannot mistake for working
  functionality — never silently mark the parent task complete while it
  contains an unbuilt piece.
- Never add fake/illustrative data (dashboard metrics, sample rows, demo
  numbers) to any screen without it being explicitly disclosed as fake in
  the walkthrough AND obviously labeled in the UI itself. Undisclosed
  fake data presented as if real is a critical-severity violation of this
  rule, not a minor gap.
- Never add a feature, screen, or element that was not part of the
  approved plan (e.g. an unrequested Dashboard) without flagging it as an
  addition and getting confirmation — scope additions are not "extra
  helpfulness," they're untracked, unreviewed surface area.
- Before marking any UI task complete in task.md, actually click through
  it end-to-end in a running browser against the real backend — not just
  confirm the code compiles or a component test passes. If auth is
  involved, actually log in as a real user via the real login flow before
  claiming RBAC or any authenticated behavior works.
- A walkthrough claiming a feature "works" or is "complete" must be
  something the user can independently verify by clicking through the
  running app themselves — if a screen only has a screenshot for part of
  a multi-step flow (e.g. 2 of 6 wizard steps), that flow is not done,
  regardless of what task.md says.

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
