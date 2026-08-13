"""Local LLM abstraction over Ollama with graceful fallback."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("services.llm")


class LocalLLM:
    """Thin Ollama client. Never hardcodes a single model name."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 60.0,
    ) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.llm_model
        self.timeout = timeout
        self._available: Optional[bool] = None

    def is_available(self) -> bool:
        try:
            with httpx.Client(timeout=3.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                self._available = response.status_code == 200
                return self._available
        except Exception:
            self._available = False
            return False

    def generate(
        self,
        prompt: str,
        *,
        system: Optional[str] = None,
        format_json: bool = False,
        temperature: float = 0.2,
    ) -> Optional[str]:
        """Return generated text, or None if Ollama is unavailable."""
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if system:
            payload["system"] = system
        if format_json:
            payload["format"] = "json"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(f"{self.base_url}/api/generate", json=payload)
                if response.status_code != 200:
                    logger.warning(
                        "Ollama generate failed status=%s body=%s",
                        response.status_code,
                        response.text[:200],
                    )
                    return None
                data = response.json()
                return (data.get("response") or "").strip() or None
        except Exception as exc:
            logger.warning("Ollama unavailable: %s", exc)
            return None


def extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    """Parse a JSON object from model output, tolerating fences."""
    if not text:
        return None
    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, flags=re.DOTALL)
    if fence:
        cleaned = fence.group(1)
    try:
        data = json.loads(cleaned)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None


llm_client = LocalLLM()
