# src/emotionics/core.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional, Protocol

from .errors import EmotionicsError, NotActivatedError, InvalidModeError,  ValidationError
from .lite import analyze_lite
from .full import analyze_full

Mode = Literal["lite", "full"]
LLMName = Literal["openai", "gemini"]  # for now

class LLMProvider(Protocol):
    def generate(self, *, prompt: str, model: str, **kwargs: Any) -> str: ...

@dataclass(frozen=True)
class EmotionicsConfig:
    provider: Optional[LLMProvider] = None
    model: str = "auto"

_DEFAULT_CONFIG: Optional[EmotionicsConfig] = None


def activate(
    *,
    provider: Optional[LLMProvider] = None,
    model: str = "auto",
    # thin wrapper options
    llm: Optional[LLMName] = None,
    api_key: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """
    Activate Emotionics.

    Simple (recommended):
        emotionics.activate(llm="openai", api_key="...", model="...")

    Advanced (explicit):
        emotionics.activate(provider=MyProvider(...), model="...")
    """
    global _DEFAULT_CONFIG

    # Prevent ambiguous responsibility boundary.
    if provider is not None and (llm is not None or api_key is not None):
        raise ValidationError(
            "activate() received both 'provider' and ('llm'/'api_key').",
            hint="Use either provider=... OR llm=... + api_key=..., not both.",
            details={"has_provider": True, "has_llm": llm is not None, "has_api_key": api_key is not None},
        )

    # Factory path
    if provider is None and llm is not None:
        if llm not in ["openai", "gemini"]:
            raise ValidationError(
                f"Unsupported llm: {llm!r}",
                hint="Currently supported: 'openai'",
                details={"llm": llm, "supported": ["openai"]},
            )
        if not api_key or not isinstance(api_key, str) or not api_key.strip():
            raise ValidationError(
                "api_key must be a non-empty string",
                hint=f"Pass your {llm.upper()} API key: emotionics.activate(llm={llm!r}, api_key='...')",
            )
        if llm == "openai":
            from .providers import OpenAIProvider
            provider = OpenAIProvider(
                api_key=api_key,
                base_url=kwargs.pop("base_url", None),
                organization=kwargs.pop("organization", None),
                project=kwargs.pop("project", None),
            )
        
        elif llm == "gemini":
            from .providers import GeminiProvider
            provider = GeminiProvider(api_key=api_key)

        # Keep wrapper strict (to avoid silently ignored params)
        if kwargs:
            unknown = ", ".join(sorted(kwargs.keys()))
            raise ValidationError(
                f"Unknown activate() parameters for llm='openai': {unknown}",
                hint="Allowed: base_url, organization, project",
                details={"unknown": sorted(kwargs.keys()), "allowed": ["base_url", "organization", "project"]},
            )

    _DEFAULT_CONFIG = EmotionicsConfig(provider=provider, model=model)


def _require_config() -> EmotionicsConfig:
    if _DEFAULT_CONFIG is None:
        raise NotActivatedError(
            "Emotionics is not activated.",
            hint="Call emotionics.activate(llm='openai', api_key='...', model='...') first "
                 "or emotionics.activate(provider=..., model=...).",
        )
    return _DEFAULT_CONFIG


def estimate(
    text: str,
    mode: Mode = "lite",
    actor: Optional[str] = None,
    language: str = "auto",
    **kwargs: Any,
) -> Dict[str, Any]:
    if not isinstance(text, str) or not text.strip():
        raise EmotionicsError("text must be a non-empty string")

    cfg = _require_config()

    if mode == "lite":
        return analyze_lite(
            text=text,
            actor=actor,
            language=language,
            provider=cfg.provider,
            model=cfg.model,
            **kwargs,
        )

    if mode == "full":
        return analyze_full(  # 更新
            text=text,
            actor=actor,
            language=language,
            provider=cfg.provider,
            model=cfg.model,
            **kwargs,
        )

    raise InvalidModeError(f"Unknown mode: {mode}")


def gyo(
    text: str,
    subject: str,
    circuit: str,          # 変更: platform -> circuit
    power_gradient: str,   # 変更: target -> power_gradient
    intent: str,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    【Kármán Line Provision 適用モジュール】
    テキストとコンテキスト（$S, V$）から、背後にある真の感情（$O$）を逆算し、
    Feel/Feign × Real/Fake の四象限マッピングと演技の差分を返します。

    Args:
        text (str): 分析対象のテキスト。
        subject (str): 発言者・主体の属性（例: "匿名ユーザー", "企業リーダー", "一般市民"）。
        circuit (str): 感情が循環する回路の構造（例: "1:1", "1:N", "N:1", "N:N"）。
        power_gradient (str): 相手との権力・情報勾配（例: "upward" (不利), "downward" (有利), "symmetrical" (対等)）。
        intent (str): 発言の具体的な意図・スタンス（例: "自己防衛", "攻撃", "共感の模索", "ステータス誇示"）。
    """
    if not isinstance(text, str) or not text.strip():
        raise EmotionicsError("text must be a non-empty string")

    cfg = _require_config()
    
    # 遅延インポートで循環参照や初期ロード時間を回避
    from .gyo import analyze_gyo

    return analyze_gyo(
        text=text,
        subject=subject,
        circuit=circuit,                 # 変更
        power_gradient=power_gradient,   # 変更
        intent=intent,
        provider=cfg.provider,
        model=cfg.model,
        **kwargs
    )

def en(
    gyo_data: Dict[str, Any],
    action_text: str,
    action_timestamp: float,
    original_timestamp: float, # ← この引数を追加
    radius: float = 15.0,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    【Kármán Line Provision 適用モジュール】
    対象空間（感情の極値）に対する外部からの不自然な介入（Hatsu）を感知するレーダー関数。
    
    Args:
        gyo_data (Dict): 対象のテキスト・極値時刻・加速度等の時系列データ。
                         (必須キー: 'text', 'peak_time', 'a_peak', 'peak_type')
        action_text (str): 外部からの介入アクションのテキスト。
        action_timestamp (float): 介入アクションが発生したタイムスタンプ(秒)。
        radius (float): 検知半径(秒)。デフォルトは人間の認知的バッファである15.0秒。
    """
    if not isinstance(action_text, str) or not action_text.strip():
        raise EmotionicsError("action_text must be a non-empty string")

    cfg = _require_config()
    
    # 遅延インポート
    from .en import analyze_en

    return analyze_en(
        gyo_data=gyo_data,
        action_text=action_text,
        action_timestamp=action_timestamp,
        original_timestamp=original_timestamp, # ← analyze_en に渡す
        radius=radius,
        provider=cfg.provider,
        model=cfg.model,
        **kwargs
    )

def lend_ears(
    audio_source: str | bytes,
    mime_type: str = "audio/mp3",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    【Kármán Line Provision 適用モジュール】
    対象の音声を最後まで黙って傾聴し、文字起こしと深層感情の推定を同時に行う。
    """
    cfg = _require_config()
    
    # 遅延インポート
    from .ears import analyze_ears

    return analyze_ears(
        audio_source=audio_source,
        mime_type=mime_type,
        provider=cfg.provider,
        model=cfg.model,
        **kwargs
    )