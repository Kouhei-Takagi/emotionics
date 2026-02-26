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