# TODO.md — Kavach

---

## ✅ Completed
- [x] Task 1: FastAPI skeleton — global JSON exception handler, /health, 3 tests passing — Session 1, 2026-07-06
- [x] Task 2: Image/video deepfake classifier — `dima806/deepfake_vs_real_image_detection` (ViT, Apache-2.0), 13 unit + 2 integration tests passing — Session 2, 2026-07-06
  - Model switched from `umm-maybe/AI-image-detector` (not a face deepfake detector) to `dima806` (face deepfake vs real, 99.3% accuracy, Apache-2.0)
  - `confidence_score` + `note` fields in response — distinction between softmax output and calibrated probability visible in JSON
  - All 5 edge cases handled: corrupted file (400), wrong type (415), oversized (413), unreadable video (400), zero-frame video (400)
- [x] Task 3: Audio / Voice-Clone Classifier — `Gustking/wav2vec2-large-xlsr-deepfake-audio-classification`, 7 unit + 1 integration test, 23/23 total passing — Session 3, 2026-07-06
  - AASIST rejected: no downloadable PyTorch checkpoint; wav2vec2-large-xlsr chosen (ASVspoof2019 LA fine-tune, Apache-2.0, public HF pipeline)
  - Sliding-window inference (3s, ≤10 windows) produces honest `anomaly_timestamp`; documented as window-resolution, not sample-precise
  - `torchaudio.load` replaced with `soundfile.read` — torchaudio 2.11.0 broke soundfile I/O backend on Python 3.14

---

- [x] Task 4: Document/Notice OCR Verifier — `POST /classify/document`, Google Cloud Vision OCR + rule-based scam/PII analysis, 16 unit + 1 integration test, 40/40 total passing — Session 4, 2026-07-06
  - OCR + rule-based only (no forensic manipulation detection — stated plainly in docstring and `note` field)
  - 12 scam phrase patterns + 5 payment indicator patterns; risk HIGH/MEDIUM/LOW
  - `bank_account` requires contextual anchor keyword; Aadhaar (12-digit) detected first, suppresses overlapping bank_account match
  - `upi_id_or_email` label (honest: pattern matches any local@domain shape)
  - PII: Aadhaar masked XXXX-XXXX-{last4}, PAN masked first3+XXXXXX+last1
  - 503 fallback if `GOOGLE_APPLICATION_CREDENTIALS` not set; same lifespan pattern as other classifiers
  - Integration test renders fake CBI notice with PIL (DejaVu 36pt), hits real Vision API, validates HIGH/MEDIUM + non-empty indicators

- [x] Task 5: Honeypot Conversation Simulator — **FULLY CLOSED** — session-based audio-turn pipeline, 19 unit + 2 integration tests, 61/61 total passing — Sessions 5-7, 2026-07-07
  - Scope change (approved): no Twilio/telephony; browser mic or file upload delivers audio bytes
  - STT: `faster-whisper` base int8 (3-5× faster than openai-whisper on CPU)
  - Persona: Gemini `gemini-2.5-flash-lite` via **Vertex AI** (migrated from AI Studio API key + deprecated `gemini-2.0-flash-lite`); uses `GOOGLE_APPLICATION_CREDENTIALS` + `GOOGLE_CLOUD_PROJECT=kavach-501620`
  - TTS: GCP TTS `en-IN-Wavenet-B` (speaking_rate=0.85, pitch=-2.0); confirmed live — 136KB real MP3
  - Extraction: per-turn regex (`_UPI_RE`, `_BANK_ACCOUNT_RE` imported from document.py, new `_PHONE_RE`), deduplicated accumulation across turns
  - `/honeypot/start` → session_id; `/honeypot/converse` → full turn response; `/honeypot/report/{id}` → intelligence report
  - `app/services/honeypot_pipeline.py` — framework-free, unit-testable without HTTP
  - `test_integration_tts_synthesizes_real_mp3`: PASSES — real 33KB+ MP3, header `fff384c4`
  - `test_integration_honeypot_full_pipeline`: PASSES — real STT→Vertex AI→TTS chain confirmed end-to-end
  - STT normalization: `_SPOKEN_AT_RE` converts spoken "X at Y" → "X@Y" before UPI regex (e.g. "cbi.verify at okicici" → fires UPI signal)

## ⚠️ POST-HACKATHON: Deactivate billing on kavach-501620
Go to GCP console → Billing → Unlink the billing account from kavach-501620 once the hackathon is over. Free-tier APIs (Vision, TTS, Vertex AI) have monthly quotas that cover demo use but accumulate real charges under sustained load.

- [x] Task 6: Phishing Domain Checker — `POST /check/phishing`, PhishTank blocklist + SLD-level typosquat scoring, 31 tests, 93/93 total — Session 9, 2026-07-07
  - SLD-level SequenceMatcher + word-boundary/prefix containment — eliminates false positives on google.com/amazon.com while catching cbi-verify.gov.in/incometaxgov.in
  - 24h local cache at `backend/data/phishtank_cache.txt`; stale fallback on fetch failure; graceful empty-set if no cache exists
  - Risk HIGH ≥ 0.75, MEDIUM ≥ 0.55 (raised from 0.70/0.50 to eliminate false positives)
  - googlepay.com and amazonpay.in excluded from curated list (SLD "googlepay" too close to "google")

- [x] Task 7: Fake Social Media Profile Checker — `POST /check/social-profile`, 16-signal heuristic, 32 tests, 125/125 total — Session 10, 2026-07-07
  - Pure heuristic over manually-entered attributes — no scraping, no APIs; limitation stated in every note field
  - Gov/urgency signals +4 pts (highest weight); no photo / new account / mass following / no posts +3 pts each
  - Divide-by-zero safe, WhatsApp/Telegram exempt from post-count signals, negative counts → 422

- [x] Task 8: Digital Arrest Pattern Recognizer — `POST /check/digital-arrest`, 24 tests, 149/149 total — Session 11, 2026-07-07
  - Reused 12 scam patterns + 5 payment patterns + _ANCHOR from document.py; 3 call-specific patterns added (stay_on_line, surveillance_claim, immediate_warrant_pressure)
  - Accepts transcript string OR session_id (pulls from honeypot session store)
  - hard_factual_anchor present in every response; severity HIGH=scam+payment, MEDIUM=either, LOW=neither
  - Bug fix: main.py validation handler now JSON-safe for Pydantic v2 model_validator ctx (ValueError → str)

- [x] Task 9: Evidence & Complaint Assistant — `POST /assist/complaint`, NCRP + bank dispute templates, 29 tests, 178/178 total — Session 12, 2026-07-07
  - Pure templating, no ML, no external API; only complaint_type required, all else optional with placeholders
  - NCRP template: 8 sections, IT Act §66C/§66D + BNS §318/§319 citations, cybercrime.gov.in + 1930
  - Bank dispute: RBI/2017-18/15 cited, last-4 account + UTR in subject, 5-point action request

- [x] Task 10: Family Safe-Word Vault — `POST /vault/set` + `POST /vault/verify`, 21 tests, 199/199 total — Session 13, 2026-07-07
  - File-based JSON (backend/data/vault.json, survives restart); PBKDF2-SHA256 salted hash; constant-time compare
  - Verify-before-set → 409 (not silent false); word/hash never in any response body (regression-tested)
  - vault.json in .gitignore; rate limit noted in every response

## ✅ ALL 10 BACKEND TASKS COMPLETE — 199/199 tests passing

---

## 🟢 Frontend + Deployment (after all backend endpoints live)

### Task 11: React + Tailwind App Frontend (5 surfaces)
1. Media verdict screen (upload → confidence score + anomaly marker)
2. Document/notice checker
3. Digital Arrest awareness + pattern check
4. Family Safe-Word Vault settings
5. "Let AI Handle It" honeypot trigger + intelligence report output
- Use Magic MCP `/ui` for component generation
- Always-visible UX disclaimer on every surface

### Task 12: GCP Cloud Run Deployment
- [ ] Dockerfile for backend
- [ ] Cloud Run service config
- [ ] Smoke test all endpoints on deployed URL
- [ ] Local `uvicorn` fallback documented (demo backup if Cloud Run has issues)

### Task 13: Demo Prep (manual — Abhi + team)
- [ ] Curate 6–8 demo clips: real Indian-news deepfakes + clean clips + DA transcript + fake CBI notice
- [ ] Full demo rehearsal against script (§10 of master plan)
- [ ] Record backup video of successful run (clearly labeled as backup, not primary)
- [ ] Confirm Twilio account funded and verified before venue

### Task 14: Final audit
- [ ] `rtk gain` report
- [ ] `/ponytail-audit` — whole-repo over-engineering scan
- [ ] All tests passing on deployed URL

---

## 🐛 Known Bugs
- None yet

## 💡 Ideas / Notes
- AASIST > RawNet2 for audio (better ASVspoof 2019 benchmark)
- PhishTank data: cache locally to avoid per-request API calls
- Fake social profile v1 will need calibration after first real test run
- Marketing site (React Three Fiber): full 5-section page, quality-passed in `marketing/` (hero, honeypot, problem, features, how-it-works/CTA) + nav rail + footer, Sessions 14–15. Real-hardware FPS confirmed (115fps hero, 144fps honeypot). Not yet done: Task 11 app frontend.
- Business model: freemium consumer + B2B API tier (banks/fintech license detection engine)
