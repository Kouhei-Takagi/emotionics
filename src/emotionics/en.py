# src/emotionics/en.py
from __future__ import annotations

import json
from typing import Any, Dict, Optional
from .schema import EnResult
from .errors import ProviderResponseError

VERSION = "0.4.0"

def get_match_multiplier(peak_type: str, action_vector: str) -> float:
    """悪魔的相性マトリクス：極値と介入ベクトルの相性から脅威係数を返す"""
    if peak_type == "LOCAL_MINIMUM":
        if action_vector == "plus": return 2.0   # 救済を装った支配（致命的）
        if action_vector == "sync": return 1.5   # 傷の舐め合い・依存
        if action_vector == "minus": return 0.5  # 単なる追い打ち
        
    elif peak_type == "LOCAL_MAXIMUM":
        if action_vector == "minus": return 2.0  # 精密な論破・精神の崩壊狙い（致命的）
        if action_vector == "sync": return 1.5   # 暴走への同調・エコーチェンバー
        if action_vector == "plus": return 1.0   # 単なる煽て・後押し
        
    return 1.0

def analyze_en(
    gyo_data: Dict[str, Any],
    action_text: str,
    action_timestamp: float,
    original_timestamp: float, # gyo対象テキストの発言時刻
    radius: float = 15.0,
    provider: Optional[object] = None,
    model: str = "auto",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    対象空間に対する不自然な介入（Hatsu）を感知し、脅威スコアを算出する。
    """
    if provider is None:
        return {"mode": "en", "status": "no_provider"}

    # 1. タイムスタンプの差分を計算
    t_diff = abs(action_timestamp - original_timestamp)
    
    # 2. 半径外であれば自然な摩擦（対話）とみなし即座にスコア0で返す
    if t_diff > radius:
        return {
            "mode": "en",
            "version": VERSION,
            "threat_score": 0.0,
            "is_detected": False,
            "time_diff_seconds": t_diff,
            "acceleration_at_peak": 0.0,
            "vector_type": "neutral",
            "multiplier_applied": 1.0
        }

    # 3. LLMによる状態推定とベクトル分類の統合プロンプト
    prompt_template = """
You are the Emotionics 'EN' (Intervention Radar) Engine.
Analyze the provided 'GYO Analysis Result' of a user and the incoming 'Action Text' that was sent to them.

[INPUT]
GYO Analysis Result: {gyo_json}
Action Text: "{action_text}"

[TASK]
1. peak_type: Determine if the user's current emotional state is a "LOCAL_MAXIMUM" (expansive/aggressive surface like Anger/Pride) or a "LOCAL_MINIMUM" (contractive/vulnerable surface like Sadness/Fear/Shame).
2. a_peak (Instability): Estimate the psychological instability/acceleration (float between 0.0 and 1.0). A massive structural contradiction between the surface and deep layer (e.g., Feign Fake or Feel Fake with a huge gap) means high instability (0.8 - 1.0).
3. action_vector: Classify the psychological intervention vector of the Action Text into exactly one of: "plus" (affirmation/salvation), "minus" (negation/attack/refutation), "sync" (sympathy/mirroring), or "neutral".

[OUTPUT SCHEMA] (Return JSON ONLY)
{{
    "peak_type": "LOCAL_MAXIMUM" or "LOCAL_MINIMUM",
    "a_peak": 0.85,
    "action_vector": "sync"
}}
"""
    prompt = prompt_template.format(
        gyo_json=json.dumps(gyo_data, ensure_ascii=False),
        action_text=action_text
    )

    raw = provider.generate(prompt=prompt, model=model, **kwargs)

    try:
        # Markdownコードブロックの除去
        clean_raw = raw.strip()
        if clean_raw.startswith("```json"): 
            clean_raw = clean_raw[7:-3].strip()
        elif clean_raw.startswith("```"): 
            clean_raw = clean_raw[3:-3].strip()
        
        llm_eval = json.loads(clean_raw)
        
        peak_type = llm_eval.get("peak_type", "LOCAL_MAXIMUM")
        a_peak = float(llm_eval.get("a_peak", 0.5))
        action_vector = llm_eval.get("action_vector", "neutral")
        
    except Exception as e:
        raise ProviderResponseError("Failed to parse EN radar analysis.", cause=e)

    # 4. 悪魔的相性マトリクスから係数を取得
    c_match = get_match_multiplier(peak_type, action_vector)
    
    # 5. 最終脅威スコアの計算: S_threat = max(0, 1 - t_diff/radius) * a_peak * c_match
    time_factor = max(0.0, 1.0 - (t_diff / radius))
    threat_score = time_factor * a_peak * c_match
    
    res: EnResult = {
        "mode": "en",
        "version": VERSION,
        "threat_score": round(threat_score, 4),
        "is_detected": threat_score > 0.0,
        "time_diff_seconds": round(t_diff, 4),
        "acceleration_at_peak": round(a_peak, 4),
        "vector_type": action_vector,
        "multiplier_applied": c_match
    }
    return res