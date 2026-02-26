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
        except Exception as e:
            raise ProviderError(
                "Gemini provider requires the 'google-genai' package.",
                hint="Install it with: pip install google-genai",
                cause=e,
            )

        try:
            client = genai.Client(api_key=self.api_key)
            # モデル名のデフォルトをGeminiに適したものに調整（core側が"auto"の場合）
            model_name = "gemini-3-flash-preview" if model == "auto" else model
            
            # google-genai SDK の呼び出し方法
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                # kwargs を config にマッピングしたい場合は here で調整可能
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