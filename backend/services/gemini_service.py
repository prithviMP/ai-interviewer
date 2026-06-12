import json
import re
from typing import Any

import google.generativeai as genai
from fastapi import HTTPException

from config import get_settings


class GeminiService:
    def __init__(self) -> None:
        settings = get_settings()
        self._model_name = settings.gemini_model
        self._configured = bool(settings.gemini_api_key)
        if self._configured:
            genai.configure(api_key=settings.gemini_api_key)
            self._model = genai.GenerativeModel(settings.gemini_model)
        else:
            self._model = None

    @property
    def is_configured(self) -> bool:
        return self._configured

    def generate_json(self, prompt: str) -> Any:
        if not self._model:
            raise HTTPException(
                status_code=503,
                detail="Gemini API key not configured. Set GEMINI_API_KEY in backend/.env",
            )

        try:
            response = self._model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.7,
                ),
            )
            text = response.text or ""
            return self._parse_json(text)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Gemini API error: {exc}") from exc

    def _parse_json(self, text: str) -> Any:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        return json.loads(cleaned)
