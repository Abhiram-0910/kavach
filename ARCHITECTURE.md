# ARCHITECTURE.md — Kavach

Claude reads this at the start of every session to orient itself in the codebase.

---

## Stack

| Layer | Technology | Why chosen |
|-------|-----------|------------|
| Backend API | FastAPI + Pydantic v2 | Async, typed; Pydantic enforces our JSON-only contract |
| App Frontend | React + Tailwind (Magic MCP `/ui`) | Matches toolchain; drag-file-in, verdict-out — no login |
| Marketing Site | React Three Fiber | Cinematic 3D landing page |
| Video/Image classifier | `umm-maybe/AI-image-detector` (ViT, HuggingFace) — local inference | FaceForensics++-derived pretrained; free; no training needed |
| Audio classifier | RawNet2 or AASIST pretrained checkpoint — local | Purpose-built spectral anomaly detection; more reliable than asking an LLM to "judge" audio |
| Document OCR | Google Cloud Vision API (free tier: 1,000 units/month) | Best OCR for messy multi-format government notice scans; Tesseract would embarrass us on demo day |
| Phishing domain check | Heuristic model + PhishTank blocklist data | No crawler needed; deterministic, checkable output |
| Fake social profile check | Heuristic classifier (feature scoring) | Buildable without scraping; rule-based initial version |
| Digital Arrest pattern matcher | Rule-based classifier (Python) over transcribed text | No ML training; deterministic, explainable, fast |
| Honeypot TTS | Google Cloud Text-to-Speech (GCP free tier) | GCP account already active; NOT ElevenLabs |
| Honeypot LLM persona | Gemini Pro API (free tier, primary) → GPT-4o (fallback only) | Gemini free tier handles persona; GPT-4o only if Gemini can't hold it convincingly |
| Honeypot telephony | Twilio (test number) | Real live audio bridging; avoids OS-level call-interception restrictions entirely |
| Honeypot STT | Whisper (local) | Free; avoids cloud STT cost |
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
│   │   └── routers/              # One file per feature domain
│   │       ├── classify.py       # Task 2+3: image/video/audio deepfake
│   │       ├── document.py       # Task 4: OCR + notice verifier
│   │       ├── phishing.py       # Task 6: phishing domain checker
│   │       ├── social.py         # Task 7: fake social profile checker
│   │       ├── digital_arrest.py # Task 8: pattern matcher
│   │       ├── evidence.py       # Task 9: complaint assistant
│   │       ├── safevault.py      # Task 10: family safe-word vault
│   │       └── honeypot.py       # Task 11: Twilio + Whisper + Gemini + TTS
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_api.py
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
5. **"Let AI Handle It" honeypot trigger** — live Twilio call → intelligence report

UX rule (always visible on every surface): *"This tool reduces risk but cannot guarantee 100% accuracy. Always verify through a second, independent channel before sending money."*

---

## Data Flow (target architecture)

```
Inbound call/media → Twilio webhook → FastAPI router
  → classifier pipeline (video | audio | image | OCR)
  → threat score + label
  → if scammer detected: honeypot persona (Whisper STT → Gemini LLM → GCP TTS)
  → response back to Twilio
```

---

## Key Architectural Decisions

- **JSON-only responses:** Global exception handlers override Starlette's defaults — no plain-text error ever escapes. Every handler returns `JSONResponse`. Non-negotiable — this is the exact failure mode that caused a 0/100 score previously.
- **Local ML inference first:** HF models run locally (free). GCP APIs used only where local is impractical (Vision OCR, TTS).
- **GCP-first for cloud services:** All cloud billing on one already-active GCP account. No new billing accounts without discussion.
- **Gemini before GPT-4o:** Free tier first; GPT-4o is the fallback, not default.
- **Pydantic `response_model=` on every endpoint:** No raw dict returns anywhere.
- **Twilio for honeypot telephony:** OS restrictions make it impossible to inject audio into a real native cellular call on Android/iOS — Twilio test number is the correct, honest solution.
- **Never use Render free tier for live demo:** This is what caused the prior failure under load. GCP Cloud Run or fully local `uvicorn` fallback.

---

## Demo Curated Clip Set (manual task — Abhi)
6–8 clips needed before demo:
- Real deepfake videos that made Indian news (fake business-leader endorsements work well)
- Real clean clips for comparison
- Simulated Digital Arrest transcript
- Fake CBI notice screenshot

---

## Environment Variables Required

```bash
# Copy .env.example to .env and fill these in
GOOGLE_CLOUD_PROJECT=
GOOGLE_APPLICATION_CREDENTIALS=   # path to GCP service account JSON
GEMINI_API_KEY=
OPENAI_API_KEY=                    # fallback only
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
DEBUG=false
```

---

## Known Technical Debt
- [ ] `/debug/crash` route — gate behind `DEBUG=true` env var before production
- [ ] Phishing domain check: PhishTank data needs a local cache or daily sync — do not call the API on every request
- [ ] Fake social profile checker: heuristic v1 will have false positives — needs a calibration pass after first test run
