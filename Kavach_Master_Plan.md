# KAVACH — AI Shield Against Digital Arrest & Deepfake Fraud
### Master Plan Document — Digital India Hackathon, SnIST
**Prepared for:** Abhi | **Team size:** 4 | **Prize:** ₹2,50,000 | **Track:** Open Innovation & Emerging Technologies (secondary fit: Digital Governance & Public Services, Fintech & Financial Inclusion)

---

## 1. Problem Statement

India is living through an unprecedented wave of AI-enabled fraud, branded in national media and by the Prime Minister himself as **"Digital Arrest"** scams — where fraudsters impersonate CBI, ED, RBI, TRAI, or police officials on video calls, using fake uniformed backdrops, forged agency logos, and AI-generated voices to coerce victims into 24–48 hour isolation and fraudulent "verification" or "bail" payments.

**Verified scale (every figure below is independently checkable):**
- A 2023 McAfee survey of 1,010 Indian adults found **47% have experienced, or know someone who has experienced, an AI voice-cloning or deepfake scam** — nearly double the global average of 25%. Of those affected, **83% suffered monetary loss, and nearly half lost over ₹50,000.**
- India lost **₹22,495 crore to reported cyber fraud in 2025** (Ministry of Home Affairs / National Cyber Crime Reporting Portal), following **₹22,845 crore in 2024**.
- India's own cybercrime coordination centre (I4C) projects true losses — accounting for underreporting — could exceed **₹1.2 lakh crore**.
- I4C reported **₹120.30 crore lost to Digital Arrest scams alone between January–April 2024**, a category that has grown sharply since.
- CERT-In has issued a dedicated public advisory on Digital Arrest scams; the Supreme Court is actively hearing a suo moto writ petition on the subject (Jan 2026).

**The validated gap:** In May 2026, the National Health Authority, IndiaAI Mission, and IISc Bengaluru ran the AB PM-JAY Auto-Adjudication Hackathon with an explicit "Document Forgery / Deepfake Detection" track — won by Team Sopa Claims, with Telangana's own RGUKT-Nuzvid taking runner-up. That validates deepfake detection as a live, government-funded national priority — but every one of those solutions was built **for insurance back-offices auditing hospital paperwork.** Separately, **Vastav AI** (TraceX Labs) is India's leading deepfake detector — built **for police investigators and cybersecurity professionals**, offered free to law enforcement, cloud-based, B2B-priced.

**Nobody is building the version for the person receiving the call, in the seconds before they decide whether to stay on the line or send the money.** That is Kavach's wedge.

---

## 2. The Solution

**Kavach** ("shield," Hindi/Sanskrit) is a citizen-facing AI protection platform, not a single detector. Three layers:

1. **Detect** — upload a suspicious video, voice note, image, or document and get an instant, evidence-backed verdict on whether it's AI-generated or forged, in plain language.
2. **Protect** — purpose-built modules that recognize the *specific* scam patterns actually happening in India right now (Digital Arrest, fake government notices, phishing domains, fake social profiles), not just generic "deepfake or not."
3. **Respond** — when something is confirmed fraudulent, Kavach closes the loop: auto-drafted complaints, a family safe-word check, and — as the demo's closing "wow" — an AI agent that can take over engagement with a scammer to waste their time and extract intelligence.

**One-line pitch:** *"The government built deepfake detection for banks and police. Kavach builds it for the person who just got the call."*

---

## 3. Why This Wins — Mapped to Judging Criteria

Both SnIST's stated criteria (real-world impact, innovation, uniqueness, superiority to existing systems) and the Smart India Hackathon's official rubric (novelty, complexity, feasibility, practicability, sustainability, scale of impact, user experience, future work potential) are addressed directly:

| Criterion | How Kavach delivers |
|---|---|
| **Real-world impact** | Directly protects the population most targeted by the fastest-growing, most currently newsworthy fraud category in India, with independently verified national statistics. |
| **Innovation / Novelty** | A citizen-facing protection *platform*, not a single detector — the honeypot response layer has no known consumer-facing equivalent anywhere researched. |
| **Uniqueness / better than existing systems** | Checked against every real, named competitor found (Vastav AI, AB PM-JAY winners, Google Pixel Scam Detection, Truecaller AI Call Scanner, CBI 'Abhay', Sanchar Saathi, Chakshu) — none target the ordinary citizen in the moment of decision. |
| **Feasibility / practicability** | Every core component runs on open-source pretrained models or free government/public APIs. Nothing depends on access we don't have. |
| **Scale of impact** | ₹22,495 crore reported national loss in 2025; the underlying scam pattern is escalating, not shrinking. |
| **Future work potential** | Explicit roadmap layer (below) gives judges a "here's where this goes next" story — this is documented to matter as much as the working demo itself. |

---

## 4. Complete Feature Scope

### 4.1 Core (must work flawlessly — this is the demo's foundation)
- **Media Verdict Engine:** upload video, image, or audio → real-time inference from a pretrained forensic classifier → "Real" / "AI-Generated" with a confidence score.
- Scoped honestly: promise a **confidence score and, for audio, an anomaly timestamp** — not a pixel-level heatmap unless the specific model used actually supports localized attribution. Overpromising here is the single fastest way to lose credibility under judge questioning.
- Mandatory UX disclaimer, always visible: *"This tool reduces risk but cannot guarantee 100% accuracy. Always verify through a second, independent channel before sending money."*

### 4.2 Part B — MUST BUILD (present as official SIH/national problem statements — non-negotiable per your instruction)
| # | Feature | SIH validation |
|---|---|---|
| 1 | **Phishing Domain Detector** | Matches official SIH statement: *"Create an intelligent system using AI/ML to detect phishing domains which imitate look and feel of genuine domains."* |
| 2 | **Fake Social Media Profile Detector** | Matches two official SIH statements: *"Fake Social Media Profile detection and reporting"* and *"Fake social media accounts and their detection."* |
| 3 | **Fake Government Notice / Document Verifier** | Matches official SIH statement: *"Creating an application to identify the presence of government-issued PII embedded in documents and data."* Directly extends this into verifying CBI/ED/RBI/TRAI notices — the exact document category driving Digital Arrest scams. |

### 4.3 Part B — ADDED BY STRATEGIC DECISION (highest demo differentiation, technically low-risk, all buildable in the available time)
| # | Feature | Why it's in |
|---|---|---|
| 4 | **"Digital Arrest" Pattern Recognizer** | Rule-based pattern matching (isolation language, fake-uniform video cues, "verification"/"bail" payment framing) that surfaces the exact government line: *no agency arrests via video call.* This is the sharpest, most current framing hook available — PM-referenced, CERT-In advisory-backed. Cheap to build (no new ML pipeline), high narrative payoff. |
| 5 | **One-Tap Evidence & Complaint Assistant** | Auto-drafts the NCRP (dial 1930) complaint and a bank dispute email from the scan result. Answers directly the "detection isn't protection" gap. Pure templating — near-zero technical risk. |
| 6 | **Family Safe-Word Vault** | Register a household safe word; a high-pressure money call prompts the user to ask for it. Trivial to build, highly memorable in a live demo, zero technical risk. |

### 4.4 Roadmap only — mention in the pitch, do NOT attempt to build for this hackathon
- Real-Time Video Call Face-Swap Shield (needs a live video inference pipeline — too much failure surface for the time available)
- Remote-Access App Install Guard (AnyDesk/RustDesk detection — deep Android Accessibility Service work, hard to demo convincingly live)
- UPI Danger Overlay / Cooling-Off Payment Nudge (same Accessibility Service complexity; no real UPI integration access)
- Voiceprint Check for known contacts (a third full ML pipeline on top of two others — deliberate scope discipline per the "don't double your failure surface" lesson from earlier review)
- Community Scam Feed / network effect layer (cannot be demoed honestly without a real user base — would require faking data, which we do not do)
- WhatsApp Forward-to-Verify Bot (WhatsApp Business API approval timelines are outside your control before the deadline)

### 4.5 The Honeypot — Kavach's closing "wow," rebuilt correctly this time
Your prior submission (F.R.I.E.N.D.S, HCL GUVI Buildathon) scored 0/100 — **not because the AI logic was bad**, but because the endpoint returned plain-text `"Too Many Requests"` instead of the required JSON `{"status", "reply"}` under load, breaking the evaluator's contract before your logic was ever tested. That is a fully understood, fully fixable engineering bug (see §6).

**What it actually does:** when a suspicious call/media is flagged, the user can opt to let an AI agent handle further engagement. The agent — a Whisper → LLM → TTS pipeline instructed to play a confused, stalling, information-seeking persona — keeps the scammer talking, extracts identifying details (UPI ID, phone number, bank account, scripted phrases), and produces a structured intelligence report.

**Honest technical scoping (non-negotiable):**
- Third-party apps **cannot** intercept and inject audio into a real native cellular call on Android or iOS — this is an OS-level restriction, not a skill gap. Do not claim otherwise in the submission.
- The buildable, honest version: **route the "scammer" through a Twilio number you control.** On stage, you call that number live; the STT → LLM → TTS pipeline runs live and unscripted — nothing about the AI's actual responses is pre-written. The only "staged" element is that it's a test line standing in for a future real telecom integration — that is honest scoping, not faking.
- **Legal note, stated once, plainly:** using this on your own test line with your own team's consent is not an issue. If this ever becomes a real product intercepting real users' real calls, India's consent-to-record norms and IT Act Section 66D (cheating by personation) require an actual legal review before shipping — not a hackathon-stage assumption.

---

## 5. Technical Architecture

| Component | Tool | Why |
|---|---|---|
| **Video/Image deepfake classifier** | Pretrained ViT/SigLIP model from Hugging Face (e.g. `umm-maybe/AI-image-detector`, trained on FaceForensics++-derived data) | Real, downloadable, no training needed under time pressure; genuine live inference. |
| **Audio/voice-clone classifier** | RawNet2 or AASIST pretrained checkpoint | Purpose-built spectral anomaly detection; more reliable than asking a general LLM to "judge" audio, which is not what LLMs are built or fine-tuned to do. |
| **Document/notice OCR** | Google Cloud Vision API (free tier: 1,000 units/month) | Most reliable OCR for messy, multi-format government notice scans; do not use raw Tesseract for this — it will embarrass you on demo day. |
| **Digital Arrest pattern matcher** | Rule-based classifier (Python) over transcribed call text | No ML training needed; deterministic, explainable, fast to build and demo. |
| **Phishing domain check** | Heuristic model + public blocklists (e.g. PhishTank data, domain-similarity scoring) | Buildable without a dedicated crawler; real, checkable output. |
| **Backend** | FastAPI | Enforces strict typed responses via Pydantic — directly prevents the exact contract failure that caused your prior 0/100. |
| **Frontend** | React + Tailwind, built with Magic MCP `/ui` | Matches your existing Claude Code toolchain; drag-file-in, verdict-out — no login, no unnecessary complexity. |
| **Honeypot telephony** | Twilio (test number) | Real, live audio bridging; avoids OS-level call-interception restrictions entirely. |
| **Honeypot voice pipeline** | Whisper (STT) → Claude/GPT (LLM persona) → ElevenLabs or equivalent (TTS) | All real inference, live, on stage. |
| **Hosting for demo** | Paid-tier Railway or Fly.io, or run fully local via `uvicorn` | **Never use Render's free tier for a live judged demo** — this is precisely what caused the prior failure under load. |
| **Version control** | GitHub | Standard practice; also lets judges inspect the endpoint if asked. |

---

## 6. Failure Audit

| Failure point | Prevention | Backup plan |
|---|---|---|
| Model misclassifies a live, untested upload | Curate and rehearse a known-good demo set of 6–8 real clips (real deepfakes from actual Indian news, real clean clips). This is standard, honest practice — every serious AI team does this, including the AB PM-JAY winners. | If a judge insists on their own random clip, frame it honestly: "here's what our tested accuracy looks like on our validation set" rather than gambling live. |
| API returns malformed response under load (your prior failure mode) | FastAPI + Pydantic response models; a global exception handler that forces **every** response — success, 400, 429, anything — into valid JSON with `Content-Type: application/json`. A `/health` endpoint judges/evaluators can hit first. | None needed if built correctly — this is a solved problem, not a risk to hedge. |
| Free-tier hosting throttles mid-demo | Paid tier (Railway/Fly.io) or fully local hosting for the live demo. | Local `uvicorn` fallback on a laptop with a hotspot — no cloud dependency at all if needed. |
| Digital Arrest pattern matcher over- or under-triggers | Keep the rule set narrow and tested against the specific, well-documented playbook (isolation + fake uniform + "verification"/"bail" payment) rather than generic keywords. | Curated demo transcript, same principle as the media classifier. |
| Twilio honeypot call fails to connect live on stage | Test the exact demo flow in the actual venue beforehand if possible; keep Twilio account funded and verified in advance. | Pre-recorded video of a successful run as the explicit fallback, clearly labeled as a backup only if the live attempt fails. |
| Judge asks "why not just use Vastav AI / the AB PM-JAY tool?" | Have the differentiation answer memorized cold: those are B2B/B2G forensic and back-office tools; Kavach is the only one aimed at the citizen in the moment of the call. | This is your strongest, most rehearsed line — don't improvise it. |
| Scope creep during build (14 total features tracked) | Only §4.1–4.3 are committed builds. §4.4 is explicitly roadmap-only — do not let build time drift there. | Ruthlessly re-cut scope at the halfway time checkpoint if any core feature is behind. |

---

## 7. Master Task List

| Task | Owner | Est. time | Dependencies |
|---|---|---|---|
| Repo init, env setup, FastAPI skeleton with strict JSON error handling | Claude Code | 1 hr | None |
| Integrate video/image deepfake classifier (HF model) | Claude Code | 3 hrs | Repo setup |
| Integrate audio voice-clone classifier | Claude Code | 3 hrs | Repo setup |
| Curate & test 6–8 demo clips (real deepfakes + real clean clips) | Abhi (manual research) | 2 hrs | Classifiers working |
| Document/notice OCR pipeline (Google Vision integration) | Claude Code | 2 hrs | Repo setup |
| Phishing domain heuristic checker | Claude Code | 2 hrs | Repo setup |
| Fake social media profile heuristic checker | Claude Code | 2 hrs | Repo setup |
| Digital Arrest rule-based pattern matcher | Claude Code | 2 hrs | Repo setup |
| One-Tap Evidence & Complaint Assistant (templating) | Claude Code | 1.5 hrs | Verdict engine working |
| Family Safe-Word Vault | Claude Code | 1 hr | None |
| Frontend build (`/ui` via Magic MCP) | Claude Code | 4 hrs | Backend endpoints live |
| Twilio honeypot number setup + Whisper→LLM→TTS pipeline | Claude Code + Abhi (Twilio account) | 4 hrs | None (parallel track) |
| `/health` endpoint + full JSON contract test suite | Claude Code | 1 hr | All endpoints built |
| Deploy to paid-tier host (Railway/Fly.io) | Abhi | 1 hr | All backend complete |
| Full demo rehearsal, timing, backup video recording | All 4 | 2 hrs | Everything deployed |
| `rtk gain` report + final Ponytail audit | Claude Code | 30 min | Build complete |

---

## 8. Time Plan

| Phase | Hours | Critical path? |
|---|---|---|
| Setup + core classifiers (video, audio) | 0–7 | **Yes** — everything depends on this |
| Document/phishing/social-profile Part B modules | 7–13 | Parallel-buildable across team members |
| Digital Arrest matcher + Evidence Assistant + Safe-Word Vault | 13–17.5 | Parallel-buildable |
| Frontend integration | 13–17 | **Yes** — needs backend endpoints live first |
| Honeypot (Twilio + voice pipeline) | 0–4, then 17–21 (integration) | Runs in parallel initially; final integration is critical path |
| Contract testing, deployment | 21–22 | **Yes** — nothing ships without this |
| Rehearsal + backups | 22–24 | **Yes** — non-negotiable, do not cut this for more features |

**Do not compress rehearsal time to add more features.** A flawless 8-feature demo beats a shaky 14-feature one, every time, per every reviewer who weighed in on this project.

---

## 9. Model Recommendation

**Use Claude Sonnet for Claude Code on this build.** It gives the best balance of speed and reliable multi-file Python/React reasoning for a time-boxed hackathon build across FastAPI, model integration, and frontend work simultaneously — Opus's extra depth isn't needed for tasks this well-specified, and Sonnet's faster iteration matters more under a hard deadline.

---

## 10. Demo Script (the 30-second wow, then the full flow)

1. **Open cold, no slides:** play an actual, real deepfake video that made Indian news (a fake business-leader endorsement). Kavach flags it in ~2 seconds: confidence score, audio anomaly marker.
2. **Immediately follow with the Digital Arrest hook:** *"This isn't hypothetical — the Prime Minister has personally warned citizens about this exact scam."* Show the pattern recognizer flagging a simulated digital-arrest-style call transcript.
3. **Show one Part B module live:** feed it a fake CBI notice screenshot — the document verifier flags the forged elements.
4. **Evidence Assistant:** one tap auto-generates the NCRP complaint draft.
5. **Close on the honeypot:** call the live Twilio number on speakerphone. The AI agent engages, stalls, extracts a fake "scammer" detail live and unscripted, and ends with a structured intelligence summary on screen.
6. **Final line:** *"The government built this for banks and police. We built it for the 47% of Indians who've already been targeted — and don't have either."*

---

## 11. Business Model

Freemium consumer app (free core detection + Part B checks) funding a **B2B API tier**: banks and fintech apps license the detection engine to screen suspicious payment-request calls before a transfer clears; telecom/UPI apps integrate it as an in-app "verify before you pay" step. The free consumer tier also builds the labeled real/fake dataset that keeps improving the model over time — the free tier funds the long-term moat.

---

## 12. Final Product Spec

A single web app (mobile-responsive) with five visible surfaces: (1) media upload verdict screen, (2) document/notice checker, (3) Digital Arrest awareness + pattern check, (4) Family Safe-Word Vault settings, (5) the "Let AI Handle It" honeypot trigger with a live intelligence report output. Every surface is backed by a real, live, independently-testable backend endpoint returning strict JSON — nothing hardcoded, nothing simulated, one disclaimer always visible.

---

## 13. First Action

```bash
mkdir kavach && cd kavach
git init
uvicorn --version   # confirm environment before writing a line of code
```

Then open Claude Code and say: *"Read this master plan document. Set up the FastAPI backend skeleton first, with strict Pydantic response models and a global JSON exception handler — this is non-negotiable given our prior hackathon failure. Confirm the `/health` endpoint works before we build anything else."*
