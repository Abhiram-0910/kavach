# AGENTS.md — Session Handoff Log

This file is updated at the END of every Claude Code session.
Claude reads this at the START of every new session to understand what happened before.

---

## Project State
**Last updated:** 2026-07-06
**Current branch:** master
**Overall status:** Tasks 1–3 complete — FastAPI skeleton, image/video classifier, audio voice-clone classifier. 23/23 tests passing.

---

## Session Log

### Session 1 — 2026-07-06
**Goal:** Bootstrap project docs + Task 1 FastAPI skeleton
**Completed:**
- [x] Filled CLAUDE.md (project name, stack, primary JSON-only rule)
- [x] Filled ARCHITECTURE.md (full cost-conscious GCP stack, folder structure, data flow)
- [x] Filled TODO.md (Task 1 sprint + full backlog through Task 5)
- [x] Created `backend/` skeleton: app/main.py, app/models/responses.py, requirements.txt, .env.example
- [x] Global exception handlers override Starlette defaults — zero plain-text escapes
- [x] `/health` → `{"status": "ok"}`, `/debug/crash` → intentional 500 for testing
- [x] 3 tests (health 200, 404, 500) — all assert JSON content-type + parseable body
- [x] All tests pass

**Decisions made:**
- Override `StarletteHTTPException` (not just `fastapi.HTTPException`) — catches 404/405 from the router before FastAPI sees it
- `TestClient(raise_server_exceptions=False)` — required so the 500 test gets the response body instead of a re-raised exception
- `/debug/crash` left in app (not test-only file) so CI can hit it; gate behind env var before prod

**Problems encountered:**
- None

**Left incomplete:**
- Nothing from Task 1

**Next session should start with:**
- Task 2: pull `umm-maybe/AI-image-detector` from HuggingFace, wire `/classify/image` and `/classify/video` endpoints

---

### Session 2 — 2026-07-06
**Goal:** Task 2 — video/image deepfake classifier

**Completed:**
- [x] Model sanity check: `umm-maybe/AI-image-detector` rejected — its own model card says "not a deepfake photo detector", recommends its successor. Three models compared; `dima806/deepfake_vs_real_image_detection` chosen.
- [x] `backend/app/routers/classify.py` — `POST /classify/image`, `POST /classify/video`
- [x] `backend/app/models/responses.py` — `ClassifyImageResponse`, `ClassifyVideoResponse`, `SuspiciousFrame`, `DISCLAIMER`, `CONFIDENCE_NOTE` constants
- [x] `backend/app/main.py` — lifespan added (eager model load on startup); classify router mounted
- [x] `backend/tests/test_classify.py` — 13 unit tests (mocked classifier) + 2 integration tests (real model, skip if not cached)
- [x] `backend/scripts/download_models.py` — one-shot pre-download script
- [x] All 15 tests pass (13 unit + 2 integration); original 3 still pass

**Decisions made:**
- `dima806/deepfake_vs_real_image_detection` over `umm-maybe`: only model actually trained on face deepfakes, 99.3% accuracy, Apache-2.0 license (best for business model), updated Jan 2025
- `confidence_score` + `note` fields: softmax/calibrated distinction is visible in the JSON, not just in docs — frontend can surface it honestly
- Video: 16-frame even-sample strategy; aggregate = mean fake_score; worst frame reported by index + score
- Lifespan eager load: model loads at startup (not lazy on first request) — avoids 10s hit on first real demo request
- Unit tests patch `app.routers.classify._classifier` — TestClient without context manager does NOT trigger lifespan, so no model download in CI
- Integration tests gated with `@requires_model` — skip gracefully on fresh machines

**Problems encountered:**
- `import numpy as np as _np` is invalid Python syntax — caught and fixed before tests ran

**Left incomplete:**
- Nothing from Task 2

**Next session should start with:**
- Task 3: Audio / Voice-Clone Classifier (AASIST pretrained checkpoint, `/classify/audio`)

---

### Session 3 — 2026-07-06
**Goal:** Task 3 — Audio / Voice-Clone Classifier

**Completed:**
- [x] Model sanity check: AASIST rejected — no downloadable PyTorch checkpoint; Gustking/wav2vec2-large-xlsr-deepfake-audio-classification chosen (wav2vec2-large-xlsr fine-tuned on ASVspoof2019 LA, Apache-2.0, public HF pipeline)
- [x] Timestamp honesty: model is whole-clip only — sliding window (3s, up to 10 evenly sampled) used to produce `anomaly_timestamp` honestly; this is documented in the `note` field and ARCHITECTURE.md
- [x] `POST /classify/audio` — file validation (type 415, size 413, silence 400, corrupted 400), torchaudio load → windowed inference → verdict + anomaly_timestamp
- [x] `ClassifyAudioResponse` added to `app/models/responses.py`
- [x] 7 audio unit tests + 1 audio integration test (all pass; skip if model not cached)
- [x] `scripts/download_models.py` updated to include audio model
- [x] **Bugfix:** `torchaudio==2.11.0+cu130` (Python 3.14) changed default I/O backend to `torchcodec` (not installed) — fixed by replacing `torchaudio.load` with `soundfile.read` for file I/O; `torchaudio.functional.resample` kept for resampling (pure math, no I/O dependency)
- [x] All 23 tests pass (3 API + 5 image + 5 video + 7 audio unit + 3 integration)

**Decisions made:**
- `soundfile.read` over `torchaudio.load`: torchaudio 2.11.0 broke soundfile backend on Python 3.14; soundfile is already a dep and handles WAV/FLAC/OGG natively
- Sliding-window anomaly_timestamp: honest scoping — timestamp is window-start resolution (3s), documented in response `note` field as "not sample-precise"
- `AUDIO_CONFIDENCE_NOTE` differs from image `CONFIDENCE_NOTE`: includes training-data caveat (ASVspoof2019 LA vs modern voice cloning)

**Problems encountered:**
- `torchaudio.load` silently switched to torchcodec backend in 2.11.0 — no fallback, no error until runtime; fixed by bypassing torchaudio I/O entirely

**Left incomplete:**
- Nothing from Task 3

**Next session should start with:**
- Task 4: Document/Notice OCR Verifier (Google Cloud Vision API, `/classify/document`)

---

### Session 1 addendum — Master Plan ingested, 2026-07-06
**Kavach_Master_Plan.md** copied and read in full. Key updates applied:
- ARCHITECTURE.md: added specific HF model name (`umm-maybe/AI-image-detector`), all 5 frontend surfaces, full router map, Twilio/Whisper pipeline, demo clip curation task, tech debt items
- TODO.md: expanded from 5 tasks to 14 — added phishing domain checker, fake social profile checker, Digital Arrest pattern matcher, Evidence & Complaint Assistant, Family Safe-Word Vault, frontend (5 surfaces), GCP Cloud Run deploy, demo prep, final audit
- All stack overrides confirmed (user > master plan): GCP Cloud Run over Railway/Fly.io, Google Cloud TTS over ElevenLabs, Gemini primary over Claude/GPT direct
- Master plan confirms: the prior 0/100 failure was plain-text "Too Many Requests" under load — our global exception handler directly fixes this
- Honeypot scoping confirmed: Twilio test number is the correct approach (OS restrictions prevent real call injection — we don't claim otherwise)
