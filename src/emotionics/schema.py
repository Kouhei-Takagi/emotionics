# src/emotionics/schema.py
from __future__ import annotations
from typing import Any, Dict, List, Literal, TypedDict

class LiteResult(TypedDict):
    mode: Literal["lite"]
    version: str
    trust: float
    surprise: float
    joy: float
    fear: float
    confidence: float

# --- Full Result Types ---

class EmotionCandidate(TypedDict):
    label: str
    score: float

class TemporalResult(TypedDict):
    direction_t1: Literal["past", "present", "future"]
    d: float

class TemporalDistribution(TypedDict):
    past: float
    present: float
    future: float

class FullResult(TypedDict):
    mode: Literal["full"]
    version: str
    candidate_emotions: List[EmotionCandidate]
    temporal: TemporalResult
    temporal_distribution: TemporalDistribution
    intensity: float
    politeness: float
    sarcasm: float
    directness: float
    honesty_cues: float

# --- Meta Result Types ---

class MetaGyoKwargs(TypedDict, total=False):
    """Only the inferred, non-null context fields to pass into gyo()."""
    subject: str
    circuit: Literal["1:1", "1:N", "N:1", "N:N"]
    power_gradient: Literal["symmetrical", "upward", "downward"]
    intent: str

class MetaResult(TypedDict):
    """Hypotheses about the speaker's *perceived* communicative context."""
    mode: Literal["meta"]
    version: str
    perspective: Literal["speaker_perceived"]
    subject: str | None
    circuit: Literal["1:1", "1:N", "N:1", "N:N"] | None
    power_gradient: Literal["symmetrical", "upward", "downward"] | None
    intent: str | None
    uncertainty: Dict[str, str]
    gyo_kwargs: MetaGyoKwargs

# --- Gyo Result Types ---

class SurfaceLayer(TypedDict):
    method: str
    perceived_emotion: str
    perceived_quadrant: str

class DeepLayer(TypedDict):
    method: str
    true_emotion_O: str
    actual_quadrant: str

class DeltaAnalysis(TypedDict):
    gap: str
    mechanism: str

class GyoResult(TypedDict):
    mode: Literal["gyo"]
    version: str
    surface_layer: SurfaceLayer
    deep_layer: DeepLayer
    delta_analysis: DeltaAnalysis

# --- En Result Types ---

class EnResult(TypedDict):
    mode: Literal["en"]
    version: str
    threat_score: float
    is_detected: bool
    time_diff_seconds: float
    acceleration_at_peak: float
    vector_type: str
    multiplier_applied: float

# --- Wave Result Types ---

class WaveTimelineItem(TypedDict):
    time_start: float
    time_end: float
    text: str
    analysis: Dict[str, Any]

class WaveResult(TypedDict):
    mode: Literal["wave"]
    version: str
    interval: float
    timeline: List[WaveTimelineItem]