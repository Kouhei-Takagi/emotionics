# src/emotionics/wave.py
from __future__ import annotations

import concurrent.futures
from typing import Any, Dict, List, Optional

from .core import estimate
from .errors import EmotionicsError
from .schema import WaveResult, WaveTimelineItem

VERSION = "0.9.0"


def analyze_wave(
    transcript_data: list[dict],
    interval: float = 15.0,
    mode: str = "lite",
    provider: Optional[object] = None,
    model: str = "auto",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    時系列のテキストデータ（トランスクリプト）を感情スコアの波（Time-Series Array）として解析します。

    Args:
        transcript_data (list[dict]): [{"text": "...", "start": 0.0, "duration": 2.0}, ...] 形式のリスト。
        interval (float): マージする時間枠（秒、デフォルト15.0秒）。
        mode (str): estimateに渡すモード ("lite" または "full")。
        provider (Optional[object]): LLMプロバイダインスタンス。
        model (str): 使用するモデル識別子。
        **kwargs (Any): estimate に渡す追加オプション（max_workers 等）。

    Returns:
        Dict[str, Any]: {
            "mode": "wave",
            "version": "0.9.0",
            "interval": float,
            "timeline": [
                {
                    "time_start": float,
                    "time_end": float,
                    "text": str,
                    "analysis": dict
                }, ...
            ]
        }
    """
    if interval <= 0:
        raise EmotionicsError("interval must be a positive number")

    if not isinstance(transcript_data, list):
        raise EmotionicsError("transcript_data must be a list of dictionaries")

    # 1. タイムスタンプ（start）と interval に基づくグループ化
    # slot_idx = int(start // interval)
    grouped: Dict[int, List[str]] = {}
    for item in transcript_data:
        if not isinstance(item, dict):
            continue

        raw_text = item.get("text", "")
        if raw_text is None:
            continue
        text = str(raw_text).strip()
        if not text:
            continue

        try:
            start = float(item.get("start", 0.0))
        except (TypeError, ValueError):
            start = 0.0

        if start < 0.0:
            start = 0.0

        slot_idx = int(start // interval)
        if slot_idx not in grouped:
            grouped[slot_idx] = []
        grouped[slot_idx].append(text)

    # チャンクリストをスロット時系列順に構築
    chunks: List[Dict[str, Any]] = []
    for slot_idx in sorted(grouped.keys()):
        merged_text = " ".join(grouped[slot_idx]).strip()
        if not merged_text:
            continue
        time_start = round(slot_idx * interval, 4)
        time_end = round((slot_idx + 1) * interval, 4)
        chunks.append({
            "slot_idx": slot_idx,
            "time_start": time_start,
            "time_end": time_end,
            "text": merged_text,
        })

    if not chunks:
        res: WaveResult = {
            "mode": "wave",
            "version": VERSION,
            "interval": float(interval),
            "timeline": [],
        }
        return res

    # 2. ThreadPoolExecutor による並列感情分析（matrix.py の実装パターンに準拠）
    max_workers = kwargs.pop("max_workers", min(10, len(chunks)))
    max_workers = max(1, max_workers)

    results: List[Any] = [None] * len(chunks)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {
            executor.submit(
                estimate,
                text=chunk["text"],
                mode=mode,
                provider=provider,
                model=model,
                **kwargs,
            ): idx
            for idx, chunk in enumerate(chunks)
        }

        # 完了したものから順次結果を取得（インデックスで元の時系列順序を維持）
        for future in concurrent.futures.as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                results[idx] = future.result()
            except Exception as exc:
                results[idx] = {"error": str(exc)}

    # 3. 出力 timeline の構築
    timeline: List[WaveTimelineItem] = []
    for idx, chunk in enumerate(chunks):
        timeline.append({
            "time_start": chunk["time_start"],
            "time_end": chunk["time_end"],
            "text": chunk["text"],
            "analysis": results[idx],
        })

    wave_res: WaveResult = {
        "mode": "wave",
        "version": VERSION,
        "interval": float(interval),
        "timeline": timeline,
    }
    return wave_res
