# AGENTS.md — Session Handoff Log

This file is updated at the END of every Claude Code session.
Claude reads this at the START of every new session to understand what happened before.

---

## Project State
**Last updated:** 2026-07-07
**Current branch:** master
**Overall status:** ✅ ALL 10 BACKEND TASKS COMPLETE — 199/199 tests passing.
Tasks 1–10: FastAPI skeleton, image/video classifier, audio classifier, document OCR verifier, honeypot simulator, phishing checker, social profile checker, digital arrest recognizer, complaint assistant, safe-word vault. Next: Task 11 — React + Tailwind frontend (5 surfaces).

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

### Session 4 — 2026-07-06
**Goal:** Task 4 — Document/Notice OCR Verifier

**Completed:**
- [x] `google-cloud-vision>=3.0.0` added to requirements.txt and installed
- [x] `ScamIndicator`, `PIIMatch`, `ClassifyDocumentResponse` added to `app/models/responses.py`
- [x] `backend/app/routers/document.py` — `POST /classify/document`
  - OCR via Google Cloud Vision API; rule-based text analysis (not forensic manipulation detection — explicitly scoped in docstring + `note` field)
  - 12 scam phrase patterns (digital_arrest, verification_payment, bail_payment, fake_agency_order, etc.)
  - 5 payment indicator patterns (upi_id_or_email, bank_account, urgent_deadline, immediate_payment, transfer_demand)
  - `bank_account` requires contextual anchor (`account|a/c|ifsc|acc no`) within 15 non-digit chars — prevents bare phone/invoice numbers from triggering
  - Aadhaar (12-digit) detected first; bank_account match suppressed when digit spans overlap — prevents double-flagging same number
  - Risk: HIGH (scam + payment), MEDIUM (scam or PII), LOW (neither)
  - Hard factual anchor appended to `note` when risk is medium/high: "No Indian government agency arrests via video call..."
  - PII masking: Aadhaar → XXXX-XXXX-{last4}, PAN → first3+XXXXXX+last1
  - 503 fallback if `GOOGLE_APPLICATION_CREDENTIALS` not set or Vision client init fails; server starts normally
- [x] `app/main.py` — `load_vision_client()` added to lifespan; document router mounted
- [x] `backend/.env.example` — already contained `GOOGLE_APPLICATION_CREDENTIALS` key
- [x] `backend/tests/test_document.py` — 16 unit tests + 1 integration test
  - Includes specific regression tests: Aadhaar not double-flagged as bank_account; plain numbers without anchor keyword don't trigger
  - Integration test renders fake CBI notice via PIL (DejaVu Bold 36pt), submits to real Vision API, validates HIGH/MEDIUM + non-empty indicators
- [x] All 40 tests pass (3 API + 5 image + 5 video + 7 audio unit + 3 classify integration + 16 document unit + 1 document integration)

**Decisions made:**
- `upi_id_or_email` label (not `upi_id`) — honest about what the pattern actually matches (any local@domain)
- `bank_account` contextual anchor prevents the most common false positive (standalone phone/invoice numbers)
- Aadhaar-first detection with span overlap suppression — prevents double-counting same number as both PII and payment indicator
- Integration test does NOT use `pytest.mark.skipif` that would hide failures — uses `requires_gcp` which skips only when env var is unset; env var IS set in this environment

**Problems encountered:**
- None

**Left incomplete:**
- Nothing from Task 4

**Next session should start with:**
- Task 5: Honeypot (Twilio + Whisper + Gemini + GCP TTS, `/honeypot/incoming`)

---

### Session 5 — 2026-07-06
**Goal:** Task 5 — Honeypot Conversation Simulator

**Scope change (approved):** No Twilio/telephony. Session-based audio-turn simulator — browser mic or file upload delivers audio bytes. ARCHITECTURE.md updated accordingly; Twilio removed from stack table entirely.

**Completed:**
- [x] `faster-whisper>=1.0.0`, `google-genai>=2.0.0` added to requirements.txt and installed
- [x] `app/services/honeypot_pipeline.py` — framework-free service layer:
  - STT: `faster-whisper` base int8 (`load_whisper_model()` at startup)
  - Persona: `gemini-2.0-flash-lite` with "Ramesh Kumar" confused-retiree system prompt (approved verbatim)
  - TTS: GCP TTS `en-IN-Wavenet-B`, speaking_rate=0.85, pitch=-2.0 (`load_tts_client()` at startup)
  - Extraction: imports `_UPI_RE`, `_BANK_ACCOUNT_RE`, `_AADHAAR_RE`, `_SCAM_PATTERNS` from document.py (ponytail: reuse not redefine); only `_PHONE_RE` (`\b(?:\+91[\s\-]?)?[6-9]\d{9}\b`) is new
  - `contains_self_disclosure()` — regex guard against persona breaking character
  - All stages return `(result, error_str|None)` for graceful degradation
- [x] `app/routers/document.py` — extracted `_UPI_RE` and `_BANK_ACCOUNT_RE` as named module-level constants (no behavior change)
- [x] `app/routers/honeypot.py` — `/honeypot/start`, `/honeypot/converse`, `/honeypot/report/{session_id}`
  - In-memory session store (UUID4 keys, no TTL for demo)
  - Unknown session_id → 404 JSON (same global handler)
  - `_merge_intel()` deduplicates signals across turns using set-based accumulation
  - Accepts: WAV/FLAC/OGG/WebM/MP4 (browser mic support), 25 MB max
- [x] `app/main.py` — `load_whisper_model()` and `load_tts_client()` added to lifespan
- [x] `app/models/responses.py` — `StartSessionResponse`, `TurnSignals`, `CumulativeIntel`, `ConverseResponse`, `TurnHistoryItem`, `ReportResponse` added
- [x] `backend/tests/test_honeypot.py` — 19 unit tests (all mocked)
  - 3-turn cumulative intel accumulation test
  - Per-stage degradation tests (STT fail, Gemini fail, TTS fail)
  - Persona self-disclosure regression (4 good + 4 bad replies)
  - Unknown session → 404 for both /converse and /report
  - `extract_signals` unit tests including false-positive guard
  - `autouse` fixture clears `_sessions` dict between tests
- [x] ARCHITECTURE.md — Twilio removed; honeypot row updated; honeypot pipeline stages table; known debt entries added
- [x] All 59 tests pass

**Decisions made:**
- `faster-whisper` over `openai-whisper`: 3-5× faster on CPU, critical for demo feel
- `gemini-2.0-flash-lite` over `gemini-pro`: faster + free tier; the persona task doesn't need a larger model
- Pattern imports from document.py not redefined: one change to regex = one place to change
- Session state in router (not pipeline): pipeline is stateless and framework-free; router owns lifecycle

**Problems encountered:**
- Initial test had `urgent_deadline` (a payment indicator) incorrectly asserted under `scripted_phrases` (which only covers `_SCAM_PATTERNS`). Fixed by adding "digital arrest" to that turn's transcript and asserting `digital_arrest` instead.

**Left incomplete:**
- TTS integration path: Cloud Text-to-Speech API not yet enabled on GCP project (`project=459418408332`). `persona_reply_audio` returns null gracefully.

**Next session should start with:**
- Task 6: Phishing Domain Checker (`/check/phishing`)

---

### Session 6 — 2026-07-06
**Goal:** Close TTS gap; add honeypot integration tests

**Completed:**
- [x] Cloud TTS API confirmed enabled — `synthesize_speech()` returns real 33KB+ MP3 (header `fff384c4`)
- [x] `requires_gcp` / `requires_full_pipeline` skip markers added to test_honeypot.py
- [x] `_make_scammer_audio()` helper: GCP TTS `en-IN-Standard-C` + LINEAR16 → WAV bytes (RIFF header) — Whisper reads natively as audio/wav
- [x] `test_integration_tts_synthesizes_real_mp3`: loads real TTS client, calls `synthesize_speech()`, verifies valid MPEG sync word — **PASSES** with GCP creds
- [x] `test_integration_honeypot_full_pipeline`: full `/honeypot/start` + `/honeypot/converse` with real WAV input; verifies all 4 stage_log success + non-null `persona_reply_audio` — **SKIPS** until `GEMINI_API_KEY` set
- [x] TODO.md and AGENTS.md updated; TTS debt entry closed
- [x] 60/60 tests pass, 1 skipped correctly

**Decisions made:**
- `LINEAR16` (not MP3) for scammer test audio: GCP TTS returns WAV with RIFF header — no ffmpeg format confusion for Whisper
- Separate TTS voice for scammer (`en-IN-Standard-C`) vs persona (`en-IN-Wavenet-B`): distinct voices, cheaper Standard tier for test runs

**Left incomplete:**
- Nothing — Task 5 fully closed in Session 7.

**Next session should start with:**
- Task 6: Phishing Domain Checker (`/check/phishing`)

---

### Session 7 — 2026-07-07
**Goal:** Migrate Gemini auth to Vertex AI; close Task 5 end-to-end

**Completed:**
- [x] `gemini-2.0-flash-lite` → `gemini-2.5-flash-lite` in `honeypot_pipeline.py` (deprecated June 1 2026)
- [x] ARCHITECTURE.md and TODO.md updated to reflect new model
- [x] Vertex AI migration: `genai.Client(api_key=...)` → `genai.Client(vertexai=True, project=..., location="us-central1")` in `generate_persona_reply`; guard changed from `GEMINI_API_KEY not set` → `GOOGLE_CLOUD_PROJECT not set`; kavach-vision service account granted `roles/aiplatform.user` on `kavach-501620`
- [x] `.env` updated with `GOOGLE_CLOUD_PROJECT=kavach-501620`
- [x] `requires_full_pipeline` skip marker updated: `GEMINI_API_KEY` → `GOOGLE_CLOUD_PROJECT`
- [x] `test_integration_honeypot_full_pipeline` — **PASSES** — full STT→Vertex AI persona→TTS chain confirmed
- [x] 61/61 tests pass, 0 skipped

**Real pipeline outputs from confirmed run:**
- **Transcript (Whisper):** `"Sir this is CBI officer, digital arrest case registered against you, pay verification fee immediately on UPICBI.verify at Oki Chichi within 24 hours or we will cancel your adhar card."`
  - Note: Whisper mangled `cbi.verify@okicici` → `"UPICBI.verify at Oki Chichi"` (no `@`) so UPI regex didn't fire; scam phrases fired correctly
- **Persona reply (Gemini 2.5-flash-lite, in character):** `"Arrey bhai, CBI officer? Digital arrest? Oh ho, meri jaan! Slow down, slow down. What is your name, sir ji? And your employee ID, department name? This is all very serious, I am feeling a little bit chest pain."`
  - Coherent, in-character, no self-disclosure, asks for scammer's identity — exactly correct persona behaviour
- **Extracted signals:** `scripted_phrases: [digital_arrest, verification_payment]`; UPI/bank/phone empty (Whisper mangling prevented UPI match)
- **TTS output:** 136,320 bytes real MP3, header `fff384c4`

**Decisions made:**
- Vertex AI over AI Studio API key: one billing account (GCP), one auth method (GOOGLE_APPLICATION_CREDENTIALS), no separate prepayment system to manage
- `GEMINI_API_KEY` removed from `.env` and `.env.example` in Session 8 — revoked credential, fully purged

**Problems encountered:**
- AI Studio API key had depleted prepayment credits — GCP billing activation does NOT fund AI Studio keys (separate system). Fixed by switching to Vertex AI.
- `gemini-2.0-flash-lite` was already deprecated and shut down June 1 2026 — model swap to `gemini-2.5-flash-lite` was required regardless of auth path

**Left incomplete:**
- Nothing from Task 5

**Next session should start with:**
- Task 6: Phishing Domain Checker (`/check/phishing`)

---

### Session 13 — 2026-07-07
**Goal:** Task 10 — Family Safe-Word Vault + Task 9 legal disclaimer amendment

**Completed:**
- [x] Task 9 amendment: `_LEGAL_NOTE` constant added to `complaint.py`; appended to footer of both `_build_ncrp()` and `_build_bank_dispute()` templates. Text: "NOTE: Legal section references are current as of this writing; verify current section numbers with the NCRP portal or a legal professional before filing, as citations can be amended."
- [x] `VaultSetResponse`, `VaultVerifyResponse` added to `app/models/responses.py`
- [x] `backend/app/routers/vault.py` created:
  - `POST /vault/set` — accepts `{safe_word: str}` (min_length=3, whitespace-only rejected by field_validator → 422); stores `{"salt": hex, "hash": hex}` to `backend/data/vault.json`; returns `{message, note}`; never echoes word
  - `POST /vault/verify` — accepts `{safe_word: str}`; returns `{matches: bool, note, disclaimer}`; returns 409 if no word set (not silent false); constant-time `hmac.compare_digest` to prevent timing attacks
  - Hash: `hashlib.pbkdf2_hmac("sha256", word_bytes, os.urandom(16) salt, 100_000 iterations)`
  - Storage: file-based JSON at `backend/data/vault.json` (survives server restart)
  - Rate limit note in every response: "No attempt limiting applied — do not expose publicly without rate limiting"
- [x] `vault.json` added to `backend/.gitignore`
- [x] `app/main.py` — vault router mounted
- [x] `backend/tests/test_vault.py` — 21 tests:
  - `autouse` fixture: `monkeypatch._VAULT_FILE` to `tmp_path/vault.json` — tests fully isolated
  - Unit: hash deterministic with same salt, differs for different words/salts, save/load roundtrip, load returns None when missing
  - API: set→verify correct (True), set→verify wrong (False), verify before set → 409, set overwrites
  - Validation: empty → 422, whitespace-only → 422, too-short (< 3 chars) → 422, missing field → 422, verify empty → 422
  - Security regression: set response never contains raw word, verify response never contains raw word, verify response never contains stored hash hex, set response never contains stored hash hex
  - Shape: set has message+note, verify has matches+note+disclaimer, all responses JSON
- [x] 199/199 tests pass (178 from Tasks 1–9 + 21 vault)

**✅ ALL 10 BACKEND TASKS COMPLETE — milestone**

**Storage + hashing decisions:**
- File-based JSON over in-memory: safe word must survive server restart (demo continuity; in-memory would lose state on restart mid-demo)
- `pbkdf2_hmac` SHA-256 over plain SHA-256: appropriate for password-like values; 100K iterations makes brute-force impractical for a demo word
- `hmac.compare_digest`: prevents timing-based hash inference — same stdlib, zero cost

**Next session should start with:**
- Task 11: React + Tailwind Frontend (5 surfaces) — activate ui-ux-pro-max skill

---

### Session 12 — 2026-07-07
**Goal:** Task 9 — Evidence & Complaint Assistant

**Completed:**
- [x] `ComplaintResponse` added to `app/models/responses.py`
- [x] `backend/app/routers/complaint.py` created:
  - `POST /assist/complaint` — pure templating, no ML, no external API, no new deps
  - `complaint_type: Literal["ncrp","bank_dispute","both"]` — only required field
  - All other fields Optional — missing fields get `[PLACEHOLDER]` strings; endpoint never crashes on missing data
  - `_build_ncrp()` — formal NCRP complaint text: complainant details, incident details, financial loss, suspect info, evidence checklist, legal citations (IT Act §66C/§66D, BNS §318/§319), cybercrime.gov.in + 1930 footer
  - `_build_bank_dispute()` — urgent first-person bank email: subject with last-4 account + UTR, account holder, disputed transaction, Digital Arrest fraud explanation, NCRP reference field, RBI Master Direction citation, 5-point action request
  - `matched_patterns` and `payment_indicators` from prior endpoint responses are forwarded and included in NCRP text
  - `_NEXT_STEPS` list: 6 items — cybercrime.gov.in, 1930, bank contact, evidence preservation, follow-up scam warning, use NCRP number for bank dispute
  - Helpline/portal guidance: framed as "report immediately — the sooner you report, the better the chance of fund recovery before money is moved further" (not false-precision hour claim)
- [x] `app/main.py` — complaint router mounted
- [x] `backend/tests/test_complaint.py` — 29 tests:
  - Unit: _build_ncrp with full input (complainant, amount, UPI ID, matched_patterns, legal sections, portal URL); minimal input (placeholders, no crash); _build_bank_dispute with full input (last-4 account, amount, NCRP ref, RBI citation, Digital Arrest mention); minimal input (no crash)
  - API: complaint_type filtering (ncrp→bank null, bank_dispute→ncrp null, both→both); full input 200; next_steps has 1930 + portal; disclaimer present
  - API: minimal input → 200, templates produced with placeholders
  - Validation: invalid complaint_type → 422, missing type → 422, negative amount → 422, response shape check
  - Forwarded fields: matched_patterns and payment_indicators appear in NCRP text
- [x] 178/178 tests pass (149 from Tasks 1–8 + 29 complaint)

**Template structures used:**
- **NCRP**: 8 sections (header, complainant, incident, description, financial loss, suspect, evidence checklist, requested action); IT Act 2000 §66C/§66D + BNS 2023 §318/§319 cited
- **Bank dispute**: subject line with last-4 + UTR, 6 sections, RBI/2017-18/15 Master Direction on Limiting Liability cited; requests account freeze + chargeback + written ack within 24h
- Both rendered as clean text with `━` dividers — copy-paste ready

**Decisions made:**
- Only `complaint_type` is required — the rest can be filled with placeholders. Users sometimes only have partial info (e.g., scam interrupted before payment), and a partial template is still useful
- `_ph()` helper returns value or bracketed placeholder — consistent across both templates, single function, no duplication
- `amount_lost: ge=0` validation — negative amounts don't make sense; zero is valid (e.g., scam intercepted before payment)

**Next session should start with:**
- Task 10: Family Safe-Word Vault (`/vault/set`, `/vault/verify`)

---

### Session 11 — 2026-07-07
**Goal:** Task 8 — Digital Arrest Pattern Recognizer

**Completed:**
- [x] `DigitalArrestResponse` added to `app/models/responses.py`
- [x] `backend/app/routers/digital_arrest.py` created:
  - `POST /check/digital-arrest` — accepts `{transcript: str}` OR `{session_id: str}` (pulls from honeypot session store)
  - **Reused from document.py** (ponytail: import, don't redefine): `_SCAM_PATTERNS` (12 patterns), `_PAYMENT_PATTERNS` (5 patterns), `_PAYMENT_TYPES`, `_ANCHOR`
  - **3 call-specific patterns added** (`_CALL_PATTERNS`): `stay_on_line` (don't hang up / stay on the line), `surveillance_claim` (we are tracking your phone / I can see your location), `immediate_warrant_pressure` (warrant being issued right now / you have X minutes)
  - Severity: HIGH = scam + payment hits, MEDIUM = either, LOW = neither — same logic as document.py but PII removed (phone numbers in transcripts ≠ PII exposure)
  - `hard_factual_anchor` field = `_ANCHOR` from document.py verbatim, always present in every response (not just medium/high)
  - session_id path: `from app.routers.honeypot import _sessions` (lazy import at call time to avoid circular import at module load); concatenates non-null turn transcripts
  - Empty transcript → 400 (endpoint check after model_validator passes); whitespace-only → 400
  - max_length=10_000 chars → 422; both fields missing → 422 (model_validator)
- [x] `app/main.py`:
  - digital_arrest router mounted
  - **Bug fixed**: validation exception handler now sanitizes Pydantic v2 model_validator `ctx["error"]` (ValueError object → str) to ensure JSON serializability — was not previously triggered because no prior endpoint used `model_validator(mode="after")` with a ValueError
- [x] `backend/tests/test_digital_arrest.py` — 24 tests:
  - Unit: DA transcript hits ≥3 scam labels and expected specific labels; clean transcript = no hits; call-specific patterns fire (stay_on_line, surveillance_claim, immediate_warrant_pressure); deduplication (same label appears once even if multiple phrases match)
  - Unit severity: high (both), medium (scam only, payment only), low (neither)
  - API: DA transcript → high severity + anchor present + matches document._ANCHOR exactly; clean → low; anchor always present regardless of severity
  - Session_id: mocked lookup, real injection into honeypot._sessions + cleanup, unknown id → 404
  - Validation: empty → 400, whitespace → 400, too long → 422, neither field → 422, JSON always
- [x] 149/149 tests pass (125 from Tasks 1–7 + 24 digital arrest)

**What was reused vs new:**
- **Reused**: `_SCAM_PATTERNS` (12), `_PAYMENT_PATTERNS` (5), `_ANCHOR` — imported from document.py, zero redefinition
- **New**: `_CALL_PATTERNS` (3 spoken-register patterns), `_DigitalArrestRequest` model with model_validator, `_resolve_transcript()` for session_id path, severity logic (same as document but minus PII term)
- **Bug fixed**: `main.py` validation handler wasn't JSON-safe for Pydantic v2 model_validator errors

**Decisions made:**
- PII excluded from severity: a phone number verbally stated in a transcript isn't a PII exposure event (unlike in a scanned document)
- Lazy import for `_sessions` from honeypot: avoids circular import at module load time while still enabling direct session lookup
- `hard_factual_anchor` present in ALL responses (not just medium/high): the user asked for this explicitly; for low-severity transcripts it still educates the user
- model_validator checks `is None` not `not self.transcript` — lets `""` pass through to endpoint for 400 (not 422)

**Next session should start with:**
- Task 9: Evidence & Complaint Assistant (`/assist/complaint`)

---

### Session 10 — 2026-07-07
**Goal:** Task 7 — Fake Social Media Profile Checker

**Completed:**
- [x] `ScoreEntry`, `CheckSocialProfileResponse` added to `app/models/responses.py`
- [x] `backend/app/routers/social_profile.py` created:
  - `POST /check/social-profile` — accepts 10 profile attribute fields, returns `{risk_level, total_score, red_flags, score_breakdown, note, disclaimer}`
  - Pure in-memory heuristic — no network calls, no scraping, no unofficial APIs; scope stated plainly in docstring and every `note` field
  - 16 scored signals: photo (no photo / stock), account age (< 30d / 30-90d), follower ratio (mass following / low ratio), zero followers, no posts / few posts, display name (digits / self-claimed legitimacy / gov impersonation), bio (gov impersonation / urgency / generic phrases), verified badge mitigation
  - Gov/urgency signals weighted +4 (not +3) — Digital Arrest scams always involve gov impersonation
  - Divide-by-zero safe: follower/following ratio only computed when `following_count > 0`
  - WhatsApp/Telegram exempt from post-count signals (no post feed)
  - `_LIMITATION_NOTE` appended to every `note` field (not just docs): "A well-resourced fake...will score LOW here. This is a coarse filter..."
  - Thresholds: HIGH ≥ 7, MEDIUM ≥ 4, LOW < 4
  - Field validation via Pydantic `ge=0` — negative counts → 422
- [x] `app/main.py` — social_profile router mounted (no lifespan changes — pure computation)
- [x] `backend/tests/test_social_profile.py` — 32 tests:
  - Obviously fake (all 4 major flags, score ≥ 7) + expected flag names
  - Obviously real (score < 4)
  - Edge cases: zero/zero followers (no crash), zero following + many followers (not suspicious), only follower=0 provided
  - Individual signal checks: stock photo, recently created, gov impersonation name/bio (≥4 pts each), urgency in bio, digits in name, 2 digits NOT flagged, self-claimed legitimacy, generic bio, verified badge reduces score, WhatsApp/Telegram exempt from post count
  - API validation: negative follower/following/post_count/age → 422, missing required field → 422, invalid platform → 422
  - API risk: obviously fake → HIGH, real-looking → LOW, gov impersonation → MEDIUM or HIGH
  - Response shape: all required fields present, breakdown entry shape, total_score matches breakdown sum, limitation note always present, content-type always JSON
- [x] 125/125 tests pass (93 from Tasks 1–6 + 32 social profile)

**Decisions made:**
- Gov/urgency points raised to 4 (not 3): Digital Arrest always involves gov impersonation — this is the single highest-value signal
- `profile_photo_is_stock` is Optional[bool] not bool: users may not know; absence doesn't score
- Post count exempt for WhatsApp/Telegram: those platforms have no public post feed concept
- `_LIMITATION_NOTE` always appended: user requirement explicitly stated note field must carry the honest limitation, not just docs

**Next session should start with:**
- Task 8: Digital Arrest Pattern Recognizer (`/check/digital-arrest`)

---

### Session 9 — 2026-07-07
**Goal:** Task 6 — Phishing Domain Checker

**Completed:**
- [x] `backend/data/.gitkeep` created (cache directory for PhishTank blocklist)
- [x] `backend/.gitignore` updated: `data/phishtank_cache.txt` excluded
- [x] `CheckPhishingResponse` Pydantic model added to `app/models/responses.py`
- [x] `backend/app/routers/phishing.py` created:
  - `POST /check/phishing` — accepts URL or bare domain, normalises hostname (www. stripped)
  - PhishTank blocklist: `http://data.phishtank.com/data/online-valid.csv`, 65K+ URLs, unauthenticated
  - Local cache: `backend/data/phishtank_cache.txt`, 24h TTL; served stale on fetch failure; empty-set graceful degradation if no cache exists
  - Similarity scoring: SLD-level SequenceMatcher + word-boundary containment + prefix/suffix containment (see below)
  - `_CURATED_DOMAINS`: 22 Indian gov/bank/payment domains (googlepay.com and amazonpay.in EXCLUDED — too close to google/amazon which are benign)
  - Risk thresholds: HIGH ≥ 0.75, MEDIUM ≥ 0.55, LOW otherwise
  - `matched_against` is null when similarity < MEDIUM threshold (not returned for low-scoring clean domains)
- [x] `backend/app/main.py` — `load_phishing_blocklist()` added to lifespan; phishing router mounted
- [x] `backend/tests/test_phishing.py` — 31 tests:
  - Domain extraction tests (bare domain, URL, www., path, empty)
  - SLD extraction tests (compound .gov.in / .co.in / .org.in; simple .com / .in)
  - Similarity scoring — HIGH: cbi-verify.gov.in, cbigov.in, incometaxgov.in, hdfcbank-login.com, axisbanks.com, cbi.gov.in.verify.com
  - Similarity scoring — LOW: google.com, amazon.com, example.com, openai.com, facebook.com
  - API: empty URL → 400, missing field → 422, clean domain → low risk, blocklisted domain → high risk, typosquat-not-blocklisted → high risk, URL-with-path normalised
  - Cache: fresh cache loads from disk; stale cache used as fallback when fetch fails; no-cache fetch-fail leaves empty set (no crash)
  - Integration: `test_integration_phishtank_live_fetch` — real HTTP fetch, skip if unavailable
- [x] 93/93 tests pass (62 from Tasks 1–5 + 31 phishing)

**Algorithm decision — SLD-level scoring:**
Full-domain SequenceMatcher caused critical false positives:
- `"google.com"` vs `"googlepay.com"` → 0.87 HIGH (FP)
- `"amazon.com"` vs `"axisbank.com"` → 0.64 MEDIUM (FP)
Fix: compare SLD-to-SLD (strip compound TLDs like .gov.in / .co.in before matching), plus two containment tiers:
- Word-boundary containment (`"cbi-verify"` contains `"cbi"` with separator) → 0.85
- Prefix/suffix containment (`"cbigov"` starts with `"cbi"`) → 0.75
SLD-only ratio catches SequenceMatcher-detectable typosquats (`"incometaxgov"` vs `"incometax"` = 0.857).
googlepay.com / amazonpay.in removed from curated list because even with SLD scoring, "google" vs "googlepay" = 0.77 which is indistinguishable from a real typosquat.

**Problems encountered:**
- Initial algorithm (full domain, 0.70/0.50 thresholds) gave massive false positives on "google.com", "amazon.com", "example.com", "openai.com" — unacceptable for production use
- Root cause: shared .com TLD inflated SequenceMatcher ratios for any pair of .com domains
- Fix: SLD-level comparison + containment checks — all false positives eliminated; all true positives preserved

**Next session should start with:**
- Task 7: Fake Social Media Profile Checker (`/check/social-profile`)

---

### Session 8 — 2026-07-07
**Goal:** Credential cleanup + STT normalization fix

**Completed:**
- [x] `GEMINI_API_KEY` removed from `.env` and `.env.example` — revoked credential fully purged from disk
- [x] Confirmed `.env` was NEVER committed (`git log -p -- backend/.env` returned empty — clean history)
- [x] All `GEMINI_API_KEY` references in code/docs updated:
  - `test_honeypot.py` docstring: `GEMINI_API_KEY` → `GOOGLE_CLOUD_PROJECT`
  - `ARCHITECTURE.md` degradation table: guard condition updated
  - `ARCHITECTURE.md` env vars section: `GEMINI_API_KEY=` removed; `GOOGLE_CLOUD_PROJECT` annotated as required for Vertex AI
  - `AGENTS.md` Session 7 stale note corrected
- [x] `_SPOKEN_AT_RE` added to `honeypot_pipeline.py` — normalizes STT "X at Y" → "X@Y" before UPI regex; applied at top of `extract_signals()`; narrow heuristic for spoken email/UPI patterns only
- [x] `test_extract_signals_upi_stt_normalization` added — confirms "UPICBI.verify at okicici" → `UPICBI.verify@okicici` fires UPI signal
- [x] Billing deactivation reminder restored to TODO.md (was lost during Task 5 edits)
- [x] 62/62 tests pass

**Decisions made:**
- Normalization applied inside `extract_signals()` (not in router): keeps the router clean; extraction is the right layer to own its own input cleanup

**Problems encountered:**
- Billing reminder had been silently lost from TODO.md during earlier edits — restored

**Next session should start with:**
- Task 6: Phishing Domain Checker (`/check/phishing`)

---

### Session 1 addendum — Master Plan ingested, 2026-07-06
**Kavach_Master_Plan.md** copied and read in full. Key updates applied:
- ARCHITECTURE.md: added specific HF model name (`umm-maybe/AI-image-detector`), all 5 frontend surfaces, full router map, Twilio/Whisper pipeline, demo clip curation task, tech debt items
- TODO.md: expanded from 5 tasks to 14 — added phishing domain checker, fake social profile checker, Digital Arrest pattern matcher, Evidence & Complaint Assistant, Family Safe-Word Vault, frontend (5 surfaces), GCP Cloud Run deploy, demo prep, final audit
- All stack overrides confirmed (user > master plan): GCP Cloud Run over Railway/Fly.io, Google Cloud TTS over ElevenLabs, Gemini primary over Claude/GPT direct
- Master plan confirms: the prior 0/100 failure was plain-text "Too Many Requests" under load — our global exception handler directly fixes this
- Honeypot scoping confirmed: Twilio test number is the correct approach (OS restrictions prevent real call injection — we don't claim otherwise)
