# src/emotionics/ears.py
from __future__ import annotations

import mimetypes
import json
import os
from typing import Any, Dict, Optional

from .errors import ProviderResponseError, EmotionicsError

VERSION = "0.5.0"

def analyze_ears(
    audio_source: str | bytes,
    mime_type: str = "audio/mp3",
    provider: Optional[object] = None,
    model: str = "auto",
    **kwargs: Any,
) -> Dict[str, Any]:
    
    # 拡張子から自動判定（指定されていない場合）
    if mime_type is None and isinstance(audio_source, str):
        guessed_type, _ = mimetypes.guess_type(audio_source)
        mime_type = guessed_type or "audio/mp3" # 判定できなければmp3を仮置き
    elif mime_type is None:
        mime_type = "audio/mp3"

    if provider is None:
        return {"mode": "ears", "status": "no_provider"}

    # 1. 音声データの読み込み
    audio_bytes: bytes
    if isinstance(audio_source, str):
        if not os.path.exists(audio_source):
            raise EmotionicsError(f"Audio file not found: {audio_source}")
        with open(audio_source, "rb") as f:
            audio_bytes = f.read()
    elif isinstance(audio_source, bytes):
        audio_bytes = audio_source
    else:
        raise EmotionicsError("audio_source must be a file path (str) or bytes.")

    # 2. ワンパス処理用のプロンプト構築（神父・占い師のUI思想を注入）
    prompt = """
You are the Emotionics 'Lend Ears' Engine.
Act as a silent, empathic listener.

[TASK]
1. Accurately transcribe the attached audio data into text in the original language.
2. Analyze the transcribed text and estimate the emotional state.

[OUTPUT SCHEMA] (Return JSON ONLY)
{
  "transcribed_text": "...",
  "candidate_emotions": [
    { "label": "Sadness", "score": 0.6 },
    { "label": "Insecurity", "score": 0.3 }
  ],
  "temporal": {
    "direction_t1": "past",
    "d": 0.5
  }
}

IMPORTANT RULES:
- "label" MUST be a valid emotion concept.
- Scores are floats in [0.0, 1.0]. Return up to 3 candidates, ordered by score descending.
- "transcribed_text" MUST contain the exact transcription of the audio.
"""

    # 3. Providerへの送信（追加引数として音声を渡す）
    raw = provider.generate(
        prompt=prompt, 
        model=model, 
        audio_bytes=audio_bytes,
        mime_type=mime_type,
        **kwargs
    )

    # 4. JSONのパース
    try:
        clean_raw = raw.strip()
        if clean_raw.startswith("```json"):
            clean_raw = clean_raw[7:-3].strip()
        elif clean_raw.startswith("```"):
            clean_raw = clean_raw[3:-3].strip()
        
        data = json.loads(clean_raw)
        
        res = {
            "mode": "ears",
            "version": VERSION,
            "transcribed_text": data.get("transcribed_text", ""),
            "candidate_emotions": data.get("candidate_emotions", []),
            "temporal": data.get("temporal", {"direction_t1": "present", "d": 0.0})
        }
        return res
        
    except Exception as e:
        raise ProviderResponseError(
            "LLM response parse failed in lend_ears mode.",
            details={"raw": raw[:1000]},
            cause=e
        )