# ARCHITECTURE.md — Kavach

Claude reads this at the start of every session to orient itself in the codebase.

---

## Stack

| Layer | Technology | Why chosen |
|-------|-----------|------------|
| Backend API | FastAPI + Pydantic v2 | Async, typed; Pydantic enforces our JSON-only contract |
| App Frontend | React + Tailwind (Magic MCP `/ui`) | Matches toolchain; drag-file-in, verdict-out — no login |
| Marketing Site | React Three Fiber | Cinematic 3D landing page |
| Video/Image classifier | `dima806/deepfake_vs_real_image_detection` (ViT, HuggingFace) — local inference | Face deepfake vs real; 99.3% accuracy; Apache-2.0 |
| Audio classifier | `Gustking/wav2vec2-large-xlsr-deepfake-audio-classification` — local | ASVspoof2019 LA fine-tune; free; Apache-2.0 |
| Document OCR | Google Cloud Vision API (free tier: 1,000 units/month) | Best OCR for messy multi-format government notice scans |
| Phishing domain check | Heuristic model + PhishTank blocklist data | No crawler needed; deterministic, checkable output |
| Fake social profile check | Heuristic classifier (feature scoring) | Buildable without scraping; rule-based initial version |
| Digital Arrest pattern matcher | Rule-based classifier (Python) over transcribed text | No ML training; deterministic, explainable, fast |
| Honeypot TTS | Google Cloud Text-to-Speech (GCP free tier) — `en-IN-Wavenet-B` | GCP account already active; NOT ElevenLabs |
| Honeypot LLM persona | `gemini-2.5-flash-lite` via **Vertex AI** (google-genai SDK, `vertexai=True`) | Uses GCP billing + service account auth (same creds as Vision/TTS). Migrated from AI Studio API key (`gemini-2.0-flash-lite` deprecated June 1 2026) |
| Honeypot transport | **Session-based audio-turn simulator (upload or browser mic, no telephony)** | Scope change from master plan (approved): no Twilio; browser mic or file upload delivers audio bytes to the same endpoint |
| Honeypot STT | `faster-whisper` base int8 (local, CPU) | 3-5× faster than openai-whisper on CPU; demo needs near-real-time latency |
| Hosting | GCP Cloud Run (free tier) | GCP account active; upgrade only if load tests show it's needed |
| Version control | GitHub | Standard; lets judges inspect endpoints if asked |

---

## Folder Structure

```
kavach/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app, global exception handler, router mounts
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── responses.py      # Shared Pydantic response models
│   │   ├── routers/              # One file per feature domain
│   │   │   ├── classify.py       # Tasks 2+3: image/video/audio deepfake
│   │   │   ├── document.py       # Task 4: OCR + notice verifier
│   │   │   ├── honeypot.py       # Task 5: session-based conversation simulator
│   │   │   ├── phishing.py       # Task 6: phishing domain checker
│   │   │   ├── social.py         # Task 7: fake social profile checker
│   │   │   ├── digital_arrest.py # Task 8: pattern matcher
│   │   │   ├── evidence.py       # Task 9: complaint assistant
│   │   │   └── safevault.py      # Task 10: family safe-word vault
│   │   └── services/
│   │       └── honeypot_pipeline.py  # STT → Persona → TTS → Extraction (framework-free)
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   ├── test_classify.py
│   │   ├── test_document.py
│   │   └── test_honeypot.py
│   ├── scripts/
│   │   └── download_models.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/                     # React + Tailwind (5 surfaces — Phase 3)
├── marketing/                    # React Three Fiber cinematic site (Phase 4)
├── CLAUDE.md
├── ARCHITECTURE.md
├── AGENTS.md
├── TODO.md
└── SKILLS.md
```

---

## Five Frontend Surfaces (final product)

1. **Media verdict screen** — upload video/audio/image → confidence score + anomaly marker
2. **Document/notice checker** — upload scan → OCR + forgery flags
3. **Digital Arrest awareness + pattern check** — transcript or call description → rule-based verdict
4. **Family Safe-Word Vault** — register/verify household safe word
5. **"Let AI Handle It" honeypot simulator** — upload scammer audio or use browser mic → persona reply audio + intelligence report

UX rule (always visible on every surface): *"This tool reduces risk but cannot guarantee 100% accuracy. Always verify through a second, independent channel before sending money."*

---

## Data Flow

```
Browser mic / file upload → POST /honeypot/converse (audio bytes)
  → faster-whisper STT → transcript
  → Gemini (Ramesh Kumar persona) → reply text
  → GCP TTS en-IN-Wavenet-B → base64 MP3
  → regex signal extraction (UPI IDs, bank accounts, phones, scam phrases)
  → ConverseResponse {transcript, reply_text, reply_audio, signals_this_turn, cumulative_intel}

Parallel: /classify/* endpoints for deepfake/document analysis
```

---

## Key Architectural Decisions

- **JSON-only responses:** Global exception handlers override Starlette's defaults — no plain-text error ever escapes. Every handler returns `JSONResponse`. Non-negotiable — this is the exact failure mode that caused a 0/100 score previously.
- **Local ML inference first:** HF models run locally (free). GCP APIs used only where local is impractical (Vision OCR, TTS).
- **GCP-first for cloud services:** All cloud billing on one already-active GCP account. No new billing accounts without discussion.
- **Gemini 2.0 Flash Lite before GPT-4o:** Free tier first; GPT-4o is never needed for the persona use case.
- **Pydantic `response_model=` on every endpoint:** No raw dict returns anywhere.
- **No telephony:** The honeypot is a session-based simulator. Real call routing (SIP, WebRTC, cellular) is a future integration — see Known Technical Debt.
- **Never use Render free tier for live demo:** GCP Cloud Run or fully local `uvicorn` fallback.
- **Pattern reuse over redefine:** `_UPI_RE` and `_BANK_ACCOUNT_RE` in `document.py` are named exports; `honeypot_pipeline.py` imports them directly. Single source of truth.

---

## Honeypot Pipeline Stages (graceful degradation)

| Stage | Fails when | Effect |
|-------|-----------|--------|
| STT (faster-whisper) | Model not loaded; audio undecipherable | `transcript=null`; Persona+TTS skipped |
| Persona (Gemini) | `GOOGLE_CLOUD_PROJECT` not set; Vertex AI API error | `persona_reply_text=null`; TTS skipped |
| TTS (GCP) | API disabled; `GOOGLE_APPLICATION_CREDENTIALS` missing | `persona_reply_audio=null`; text still returned |
| Extraction (regex) | (extremely unlikely) regex engine error | `signals_this_turn` zeroed; session still saved |

All four stages always produce a `stage_log` entry. Session state is saved with whatever was recovered.

---

## Demo Curated Clip Set (manual task — Abhi)
6–8 clips needed before demo:
- Real deepfake videos that made Indian news (fake business-leader endorsements work well)
- Real clean clips for comparison
- Simulated Digital Arrest scammer audio clip (for honeypot demo)
- Fake CBI notice screenshot

---

## Environment Variables Required

```bash
# Copy .env.example to .env and fill these in
GOOGLE_CLOUD_PROJECT=              # GCP project ID (e.g. kavach-501620) — required for Vertex AI Gemini
GOOGLE_APPLICATION_CREDENTIALS=   # path to GCP service account JSON — required for Vision, TTS, Vertex AI
OPENAI_API_KEY=                    # fallback only — not currently used
DEBUG=false
```

---

## Known Technical Debt
- [ ] `/debug/crash` route — gate behind `DEBUG=true` env var before production
- [ ] Phishing domain check: PhishTank data needs a local cache or daily sync — do not call the API on every request
- [ ] Fake social profile checker: heuristic v1 will have false positives — needs a calibration pass after first test run
- [ ] Honeypot telephony: real telecom-level call routing (SIP trunk, WebRTC bridge, or Twilio Voice) is a future integration. Current scope is session-based audio upload. Adding real call routing requires: a public HTTPS endpoint, a phone number, and either Twilio Programmable Voice or a SIP provider.
- [x] Honeypot TTS: Cloud Text-to-Speech API confirmed enabled; `persona_reply_audio` returns real 136KB MP3. ✓
- [x] Honeypot Gemini auth: migrated from AI Studio API key to Vertex AI (`vertexai=True`, `GOOGLE_CLOUD_PROJECT=kavach-501620`). Full pipeline integration test passes. ✓
- [ ] Session TTL: honeypot sessions are in-memory with no expiry. Add TTL eviction before production to avoid unbounded memory growth.
