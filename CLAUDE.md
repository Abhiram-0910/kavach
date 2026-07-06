# CLAUDE.md — Kavach

## Project Overview
**What this project does:** AI-powered deepfake and scam detection system — classifies video, audio, image, and OCR content; runs a honeypot persona over phone/chat to catch scammers.
**Stack:** FastAPI backend + React/Tailwind functional app UI + separate React Three Fiber cinematic marketing site
**Current phase:** Phase 1 — Core Classifiers
**Primary rule:** EVERY response — success, 400, 429, 500, anything — must be valid JSON with Content-Type: application/json, enforced by a global exception handler. A prior hackathon scored 0/100 because one error response wasn't valid JSON. This must never happen again.

---

## Read These First (Every Session)
- `ARCHITECTURE.md` — codebase map, key decisions, folder structure
- `AGENTS.md` — what was done in previous sessions
- `TODO.md` — what needs to be done next

Global rules from `~/.claude/CLAUDE.md` apply unless overridden below.

---

## Project-Specific Rules

### Stack Constraints
- Do not add new dependencies without asking first
- All API routes must have Pydantic response models — no raw dicts returned from endpoints
- Use environment variables for all API keys — never hardcode
- Log token usage for all LLM API calls

### Forbidden
- Plain-text error responses anywhere — every exception must be caught and returned as JSON
- Hardcoded API keys or secrets
- Adding Railway/Fly.io, ElevenLabs, or any non-GCP hosting without discussion
- New paid services — only Twilio is paid; everything else uses GCP free tier or free HF models

### Preferred Patterns
- All async functions must have try/except at the boundary layer (routers)
- Pydantic v2 models for all request/response schemas
- Separate routers per feature domain (health, classify, honeypot, etc.)

---

## Workflow for This Project

### Starting a Session
1. Read AGENTS.md — understand what was done
2. Read TODO.md — pick the next task
3. Read ARCHITECTURE.md — orient yourself in the codebase
4. State your plan before writing any code
5. Confirm scope: touch only files needed for this task

### Ending a Session
1. Run all tests — fix failures before stopping
2. Run linter/type checker
3. Update AGENTS.md — what you did, what changed
4. Update TODO.md — cross off done, add new items discovered
5. Run `rtk gain` — report token savings

---

## Testing Requirements
- Unit tests for all business logic
- Integration tests for all API endpoints
- Run: `cd backend && python -m pytest tests/ -v`
