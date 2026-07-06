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

## 🔴 Current Sprint — Task 4: Document / Notice OCR Verifier

### Task 4: Document / Notice OCR Verifier
- [ ] Google Cloud Vision API integration
- [ ] `/classify/document` — accepts image/PDF scan, returns OCR text + forgery flag list
- [ ] Target: CBI/ED/RBI/TRAI notices — exactly the Digital Arrest document category
- [ ] Unit tests mock GCP Vision; integration test uses a real scan

### Task 5: Honeypot — Twilio + Whisper + Gemini + GCP TTS
- [ ] Twilio webhook endpoint `/honeypot/incoming`
- [ ] Whisper STT on incoming audio chunk
- [ ] Gemini Pro persona (confused, stalling, information-seeking character)
- [ ] GCP TTS response back through Twilio
- [ ] Structured intelligence report: UPI ID, phone, bank account, scripted phrases extracted
- [ ] Tests (mock Twilio + Gemini)

### Task 6: Phishing Domain Checker
- [ ] Heuristic model: domain-similarity scoring + PhishTank blocklist (cache locally, daily sync)
- [ ] `/check/phishing` — accepts domain string, returns risk score + matched pattern
- [ ] Tests

### Task 7: Fake Social Media Profile Checker
- [ ] Heuristic feature scoring (account age, post frequency, follower/following ratio, profile completeness)
- [ ] `/check/social-profile` — accepts profile URL or JSON blob, returns risk score
- [ ] Tests

### Task 8: Digital Arrest Pattern Recognizer
- [ ] Rule-based classifier over call transcript text
- [ ] Rules: isolation language, fake-uniform video cues, "verification"/"bail" payment framing
- [ ] `/check/digital-arrest` — accepts transcript string, returns match list + severity
- [ ] Surface official line: *"No agency arrests via video call"*
- [ ] Tests (use documented Digital Arrest playbook phrases)

### Task 9: Evidence & Complaint Assistant
- [ ] Template engine: NCRP (dial 1930) complaint draft + bank dispute email
- [ ] `/assist/complaint` — accepts scan result JSON, returns pre-filled complaint text
- [ ] Pure templating, no ML

### Task 10: Family Safe-Word Vault
- [ ] Store/retrieve household safe word (in-memory or simple file store for demo)
- [ ] `/vault/set` and `/vault/verify` endpoints
- [ ] Tests

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
- Marketing site (React Three Fiber): dark theme, 3D shield animation, particle effects — build last
- Business model: freemium consumer + B2B API tier (banks/fintech license detection engine)
