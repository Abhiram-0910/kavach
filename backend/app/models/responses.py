from typing import Any, Literal, Optional
from pydantic import BaseModel

DISCLAIMER = (
    "This tool reduces risk but cannot guarantee 100% accuracy. "
    "Always verify through a second, independent channel before sending money."
)
CONFIDENCE_NOTE = (
    "Raw softmax output for the predicted class (0–1). "
    "Not a calibrated probability — treat as a signal, not a percentage chance."
)


class HealthResponse(BaseModel):
    status: str


class ErrorResponse(BaseModel):
    error: str
    status_code: int
    detail: Any = None


class SuspiciousFrame(BaseModel):
    frame_index: int
    fake_score: float


class ClassifyImageResponse(BaseModel):
    verdict: Literal["real", "ai_generated"]
    confidence_score: float
    note: str
    model: str
    disclaimer: str


class ClassifyVideoResponse(BaseModel):
    verdict: Literal["real", "ai_generated"]
    confidence_score: float
    note: str
    frames_sampled: int
    most_suspicious_frame: SuspiciousFrame
    model: str
    disclaimer: str


class ClassifyAudioResponse(BaseModel):
    verdict: Literal["genuine", "spoof"]
    confidence_score: float
    note: str
    # Start time (seconds) of the most suspicious audio window.
    # None only when audio is shorter than one analysis window (< 3s).
    anomaly_timestamp: Optional[float]
    model: str
    disclaimer: str


class ScamIndicator(BaseModel):
    type: str
    matched_text: str


class PIIMatch(BaseModel):
    type: Literal["aadhaar", "pan"]
    masked_value: str


class ClassifyDocumentResponse(BaseModel):
    ocr_text: str
    pii_detected: list[PIIMatch]
    scam_indicators: list[ScamIndicator]
    risk_level: Literal["low", "medium", "high"]
    note: str
    disclaimer: str


# ── Phishing check model ─────────────────────────────────────────────────────

class CheckPhishingResponse(BaseModel):
    domain: str
    in_blocklist: bool
    blocklist_match: Optional[str]    # matched blocklist entry domain; null when not in list
    similarity_score: float            # 0.0–1.0 vs curated Indian gov/bank domain list
    matched_against: Optional[str]    # curated domain with highest similarity; null when < threshold
    risk_level: Literal["low", "medium", "high"]
    note: str
    disclaimer: str


# ── Vault ─────────────────────────────────────────────────────────────────────

class VaultSetResponse(BaseModel):
    message: str
    note: str


class VaultVerifyResponse(BaseModel):
    matches: bool
    note: str
    disclaimer: str


# ── Complaint assistant ────────────────────────────────────────────────────────

class ComplaintResponse(BaseModel):
    ncrp_complaint_text: Optional[str]
    bank_dispute_text: Optional[str]
    next_steps: list[str]
    disclaimer: str


# ── Digital Arrest pattern recognizer ────────────────────────────────────────

class DigitalArrestResponse(BaseModel):
    matched_patterns: list[str]
    payment_indicators_found: list[str]
    severity: Literal["low", "medium", "high"]
    hard_factual_anchor: str
    note: str
    disclaimer: str


# ── Social profile check model ────────────────────────────────────────────────

class ScoreEntry(BaseModel):
    flag: str
    points: int
    reason: str


class CheckSocialProfileResponse(BaseModel):
    risk_level: Literal["low", "medium", "high"]
    total_score: int
    red_flags: list[str]
    score_breakdown: list[ScoreEntry]
    note: str
    disclaimer: str


# ── Honeypot models ───────────────────────────────────────────────────────────

class StartSessionResponse(BaseModel):
    session_id: str


class TurnSignals(BaseModel):
    upi_ids: list[str]
    phone_numbers: list[str]
    bank_accounts: list[str]
    scripted_phrases: list[str]


class CumulativeIntel(BaseModel):
    upi_ids: list[str]
    phone_numbers: list[str]
    bank_accounts: list[str]
    scripted_phrases: list[str]


class ConverseResponse(BaseModel):
    session_id: str
    turn: int
    transcript: Optional[str]            # null when STT fails
    persona_reply_text: Optional[str]    # null when Persona fails or STT fails
    persona_reply_audio: Optional[str]   # base64 MP3; null when TTS fails/unavailable
    signals_this_turn: TurnSignals
    cumulative_intel: CumulativeIntel
    stage_log: list[str]                 # 4 entries: STT / Persona / TTS / Extraction


class TurnHistoryItem(BaseModel):
    turn: int
    transcript: Optional[str]
    persona_reply: Optional[str]


class ReportResponse(BaseModel):
    session_id: str
    turn_count: int
    cumulative_intel: CumulativeIntel
    turn_history: list[TurnHistoryItem]
