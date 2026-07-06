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
