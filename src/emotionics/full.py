# src/emotionics/full.py
from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from .schema import FullResult
from .errors import ProviderResponseError

VERSION = "0.2.1"

# JSONの読み込み（ライブラリ内のパスを想定）
def _load_emotions_metadata() -> Dict[str, Any]:
    path = os.path.join(os.path.dirname(__file__), "assets", "emotions.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # 予期せぬエラーを防ぐためのフォールバック
        return {"emotions": []}

def analyze_full(
    text: str,
    actor: Optional[str] = None,
    language: str = "auto",
    provider: Optional[object] = None,
    model: str = "auto",
    **kwargs: Any,
) -> Dict[str, Any]:
    if provider is None:
        # 設定がない場合のデフォルト（実際にはcore側でチェックされます）
        return {"mode": "full", "status": "no_provider"}

    metadata = _load_emotions_metadata()
    allowed_labels = [e["name"] for e in metadata.get("emotions", [])]
    
    # 軸情報のテキスト化（LLMへの指示用）
    axes_desc = json.dumps(metadata.get("axis_spec", {}), indent=2)

    prompt_template = """
You are an Emotionics feature extractor.

You must classify emotions ONLY using the allowed Emotionics labels provided below.
Do NOT invent labels and do NOT use synonyms: always output the canonical label from the list.

[AXES_SPEC]
{axes_block}

[ALLOWED_LABELS]
{allowed_labels}

[OUTPUT_SCHEMA] (Return JSON ONLY)
{{
  "candidate_emotions": [
    {{ "label": "Anger", "score": 0.55 }},
    {{ "label": "Joy",   "score": 0.45 }}
  ],
  "temporal": {{
    "direction_t1": "past",
    "d": 0.62
  }},
  "temporal_distribution": {{
    "past": 0.20,
    "present": 0.70,
    "future": 0.10
  }},
  "intensity": 0.7,
  "politeness": 0.8,
  "sarcasm": 0.1,
  "directness": 0.6,
  "honesty_cues": 0.7
}}

IMPORTANT RULES:
- "label" MUST be one of the allowed labels above.
- Scores are floats in [0.0, 1.0] and should sum to <= 1.0.
- Return at most 5 candidate_emotions, ordered by score descending.
- Output MUST be valid JSON, with no extra commentary or text.
- "temporal_distribution" MUST have keys: past, present, future.
- Output MUST include "temporal" with keys: "direction_t1" and "d".
- "temporal.direction_t1" MUST be exactly one of: "past", "present", "future".
- "temporal.d" MUST be a float in [0.0, 1.0].
- Interpret "temporal.direction_t1" as the speaker's referenced time.

Text: {text}
"""
    prompt = prompt_template.format(
        axes_block=axes_desc,
        allowed_labels=", ".join(allowed_labels),
        text=text
    )

    raw = provider.generate(prompt=prompt, model=model, **kwargs)

    try:
        data = json.loads(raw)
        # 基本的な構造チェックとマッピング
        res: FullResult = {
            "mode": "full",
            "version": VERSION,
            **data
        }
        return res
    except Exception as e:
        raise ProviderResponseError(
            "LLM response parse failed in full mode.",
            details={"raw": raw[:1000]},
            cause=e
        )