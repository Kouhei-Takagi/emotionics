# src/emotionics/providers/gemini.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from ..errors import ProviderError

@dataclass
class GeminiProvider:
    api_key: str

    def generate(self, *, prompt: str, model: str, **kwargs: Any) -> str:
        try:
            from google import genai
            from google.genai import types # バイナリデータ用に追加
        except Exception as e:
            raise ProviderError(
                "Gemini provider requires the 'google-genai' package.",
                hint="Install it with: pip install google-genai",
                cause=e,
            )

        try:
            client = genai.Client(api_key=self.api_key)
            model_name = "gemini-3-flash-preview" if model == "auto" else model
            
            # --- ここからマルチモーダル対応 ---
            contents = []
            audio_bytes = kwargs.get("audio_bytes")
            mime_type = kwargs.get("mime_type", "audio/mp3")
            
            if audio_bytes:
                # 音声データがある場合はPartオブジェクトとして追加
                contents.append(
                    types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
                )
            
            # プロンプト（テキスト指示）を追加
            contents.append(prompt)
            # --- ここまで ---

            response = client.models.generate_content(
                model=model_name,
                contents=contents, # 配列を渡す
            )
            
            if not response.text:
                raise ProviderError("Gemini returned an empty response.")
                
            return response.text
        except Exception as e:
            raise ProviderError(
                "Gemini request failed (using google-genai).",
                hint="Check your API key, model name, and network connection.",
                cause=e,
                details={"model": model},
            )