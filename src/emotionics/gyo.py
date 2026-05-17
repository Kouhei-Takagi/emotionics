# src/emotionics/gyo.py
from __future__ import annotations

import json
from typing import Any, Dict, Optional

from .schema import GyoResult
from .errors import ProviderResponseError
from .full import analyze_full  # 表層分析のために内部で呼び出す

VERSION = "0.4.0" # パッケージバージョンに合わせて更新

# =====================================================================
# Emotionics 3.0 Circuit Theory & 2.0 Inversion Model Integration
#
# 【使い方と意図】
# 旧バージョンのように「twitter」「boss」といった具体的なプラットフォーム名や
# 相手の名前をライブラリ側で推測・変換（MAP）するアプローチは廃止しました。
# 理由は、同じプラットフォームでも使われ方によって構造が変化するためです。
#
# 開発者（ユーザー）は、以下の抽象化された「構造パラメータ」を直接指定します。
# これにより、未知のSNSや新しい組織構造にも柔軟に対応できます。
#
# 1. circuit (回路構造): 
#    - "1:1" (個人間対話、DMなど)
#    - "1:N" (一方的な発信、演説、インフルエンサーなど)
#    - "N:1" (炎上、集団からの非難など)
#    - "N:N" (オープンネットワーク、SNSのタイムラインなど)
#
# 2. power_gradient (権力・情報勾配): 
#    - "upward" (下位から上位への発信、防御や言い訳になりやすい)
#    - "downward" (上位から下位への発信、権力の行使)
#    - "symmetrical" (対等な関係)
#
# 3. intent (意図/スタンス): 
#    - 抽象化せず、「自己防衛」「攻撃」「共感の模索」「ステータス誇示」など
#      具体的なシチュエーションをそのまま入力します。
# =====================================================================

def analyze_gyo(
    text: str,
    subject: str,
    circuit: str,          # 変更: platform -> circuit
    power_gradient: str,   # 変更: target -> power_gradient
    intent: str,           # そのまま抽象化せずに利用
    provider: Optional[object] = None,
    model: str = "auto",
    **kwargs: Any,
) -> Dict[str, Any]:
    
    if provider is None:
        return {"mode": "gyo", "status": "no_provider"}

    # 入力変数の正規化（LLMへ渡す前のクリーニング）
    c_norm = circuit.upper().strip()
    p_norm = power_gradient.lower().strip()
    i_norm = intent.strip()

    # 1. 表層分析（Surface Layer）の実行
    # まず、一般大衆がこのテキストをどう受け取るか（表の感情）を estimate() と同じロジックで取得します。
    surface_result = analyze_full(text=text, provider=provider, model=model, **kwargs)
    
    # 候補から最もスコアの高い感情をピックアップ（安全のためフォールバックを用意）
    top_surface_emotion = surface_result.get("candidate_emotions", [{"label": "Unknown"}])[0]["label"]

    # 2. 深層・差分分析（Deep & Delta Layer）のためのプロンプト
    # 【意図】
    # Emotionics 2.0の「反転式」と「四象限モデル」のルールをコンテキストとして明示的に注入し、
    # LLMが単なる「推測」ではなく「理論に基づいた逆算（Backtracking）」を行うように強制します。
    prompt_template = """
You are the Emotionics 2.0/3.0 'GYO' (Backtracking & Observation) Engine.
Analyze the following text based on the provided structural context to deduce the TRUE hidden emotion (O) and the acting strategy.

[INPUT]
Text: "{text}"
Subject: "{subject}"
Circuit Structure: {circuit}
Power Gradient: {power_gradient}
Intent/Stance: {intent}

[SURFACE OBSERVATION]
General public perceives this as: {surface_emotion}

[EMOTIONICS INSTRUCTIONS]
1. Subject Profiling: 
   Determine if the subject is in a high-power or low-power state, and their risk/stake level based on the Circuit and Power Gradient.

2. Emotionics 2.0 Inversion Model (Backtracking):
   Apply the following inversion formulas to deduce the deep emotion:
   - Fear -> Pride (Acting overly proud to hide fear/vulnerability)
   - Shame -> Anger (Converting unfaceable shame into righteous anger)
   - Uncertainty -> Overconfidence (Masking a lack of certainty with extreme confidence)
   - Doubt -> Excessive Claim (Making absolute statements to counter internal doubt)

3. Determine the 'Feel/Feign x Real/Fake' Quadrant:
   Classify the emotional mechanism into one of the following four quadrants:
   - Feel Real: Genuine emotion from within (Common in '1:1' and 'symmetrical' circuits).
   - Feel Fake: Emotional contagion or "groupthink", mistaking external pressure for internal feeling (Common in 'N:N' circuits).
   - Feign Real: Strategic suppression or expression of a real emotion (Common in diplomacy or negotiation).
   - Feign Fake: Pure performance or manipulation (Common in '1:N' broadcasts or 'upward' defense).

4. Output ONLY valid JSON matching the schema below. Do not include markdown formatting.

[OUTPUT SCHEMA]
{{
    "deep_layer": {{
        "method": "emotionics.gyo()",
        "true_emotion_O": "...",
        "actual_quadrant": "..."
    }},
    "delta_analysis": {{
        "gap": "...",
        "mechanism": "..."
    }}
}}
"""
    prompt = prompt_template.format(
        text=text,
        subject=subject,
        circuit=c_norm,
        power_gradient=p_norm,
        intent=i_norm,
        surface_emotion=top_surface_emotion
    )

    # プロバイダーを通じたLLMへのリクエスト実行
    raw = provider.generate(prompt=prompt, model=model, **kwargs)

    # 3. 結果のパースと結合
    try:
        # Markdownのコードブロックが含まれている場合のクリーニング
        clean_raw = raw.strip()
        if clean_raw.startswith("```json"):
            clean_raw = clean_raw[7:-3].strip()
        elif clean_raw.startswith("```"):
            clean_raw = clean_raw[3:-3].strip()
        
        deep_data = json.loads(clean_raw)
        
        res: GyoResult = {
            "mode": "gyo",
            "version": VERSION,
            "surface_layer": {
                "method": "emotionics.estimate(mode='full')",
                "perceived_emotion": top_surface_emotion,
                "perceived_quadrant": "Feel Real Emotion (Assumed by public)"
            },
            "deep_layer": deep_data.get("deep_layer", {}),
            "delta_analysis": deep_data.get("delta_analysis", {})
        }
        return res
        
    except Exception as e:
        raise ProviderResponseError(
            "LLM response parse failed in gyo mode.",
            details={"raw": raw[:1000]},
            cause=e
        )