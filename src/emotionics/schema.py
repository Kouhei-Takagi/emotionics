# src/emotionics/schema.py
from __future__ import annotations
from typing import Literal, TypedDict, List

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