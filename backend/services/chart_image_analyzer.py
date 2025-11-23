"""Chart Image Analyzer
======================

Uses OpenAI's multimodal Responses API to analyze chart screenshots and return
structured pattern information the agent can reason about.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


DEFAULT_SYSTEM_PROMPT = (
    "You are a professional market technician. Analyze the provided chart image "
    "and return ONLY a JSON object describing any technical chart, price-action, "
    "or candlestick patterns you observe. Focus on well-known formations such as "
    "head and shoulders, triangles, wedges, double tops/bottoms, flags, gaps, "
    "bullish/bearish candlesticks, support/resistance interactions, volume cues, "
    "and trend changes."
)


DEFAULT_USER_PROMPT = """
Identify every clear chart pattern. For each pattern return: pattern_id, category (chart_pattern, price_action, or candlestick),
bias (bullish, bearish, neutral), confidence (0-100), evidence (concise text), recommended_action (watch, consider_entry,
wait_confirmation, take_profit), and any key support/resistance levels you observe.

Return JSON in this format:
{
  "patterns": [
    {
      "pattern_id": "head_and_shoulders",
      "category": "chart_pattern",
      "bias": "bearish",
      "confidence": 82,
      "evidence": "Right shoulder forming below prior high with neckline near 410.",
      "recommended_action": "watch",
      "key_levels": {"support": [405.0], "resistance": [420.0]}
    }
  ],
  "summary": "Bearish reversal pressure building."
}

If no patterns are visible, return {"patterns": [], "summary": "No clear patterns"}.
"""


class VisionModelConfig:
    """Configuration for a specific vision model."""

    def __init__(
        self,
        name: str,
        model_id: str,
        detail: str = "auto",
        temperature: float = 0.2,
    ) -> None:
        self.name = name
        self.model_id = model_id
        self.detail = detail
        self.temperature = temperature


DEFAULT_MODEL_MAP = {
    "gpt-5-mini": VisionModelConfig(name="gpt-5-mini", model_id="gpt-5-mini", detail="high", temperature=0.2),
    "gpt-4.1": VisionModelConfig(name="gpt-4.1", model_id="gpt-4.1", detail="high", temperature=0.15),
    "gpt-4.1-mini": VisionModelConfig(name="gpt-4.1-mini", model_id="gpt-4.1-mini", detail="auto", temperature=0.1),
}


class ChartImageAnalyzer:
    """Wrapper around OpenAI vision models for chart analysis."""

    def __init__(
        self,
        model: Optional[str] = None,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        available_models: Optional[Dict[str, VisionModelConfig]] = None,
    ) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required for chart analysis")

        self.client = AsyncOpenAI(api_key=api_key)
        self.models = available_models or DEFAULT_MODEL_MAP
        self.current_model_key = self._resolve_model_key(model)
        self.system_prompt = system_prompt

    async def analyze_chart(
        self,
        image_base64: str,
        user_context: Optional[str] = None,
        max_retries: int = 2,
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyze a chart image and return structured pattern data."""

        if not image_base64:
            raise ValueError("image_base64 is required")

        model_key = self._resolve_model_key(model_name)
        config = self.models[model_key]

        cleaned_image = image_base64.strip()
        mime_type = "image/png"
        if cleaned_image.startswith("data:image"):
            # Preserve MIME type and strip data URL prefix
            try:
                header, cleaned_image = cleaned_image.split(',', 1)
                mime_type = header.split(';', 1)[0].split(':', 1)[1] or mime_type
            except (IndexError, ValueError):
                cleaned_image = cleaned_image.split(',', 1)[-1]
        image_data_url = f"data:{mime_type};base64,{cleaned_image}"

        prompt = user_context.strip() if user_context else DEFAULT_USER_PROMPT

        last_error: Optional[Exception] = None
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    "Analyzing chart image with %s (attempt %d/%d)",
                    config.model_id,
                    attempt,
                    max_retries,
                )

                response = await self.client.responses.create(
                    model=config.model_id,
                    # Note: temperature parameter not supported by Responses API
                    input=[
                        {
                            "role": "system",
                            "content": [
                                {"type": "input_text", "text": self.system_prompt}
                            ],
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "input_text", "text": prompt},
                                {
                                    "type": "input_image",
                                    "image_url": image_data_url,
                                    "detail": config.detail,
                                },
                            ],
                        },
                    ],
                )

                text = self._extract_response_text(response)
                return self._parse_response(text)

            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Chart analysis attempt %d/%d failed: %s",
                    attempt,
                    max_retries,
                    exc,
                )

        raise RuntimeError(f"Chart analysis failed after {max_retries} attempts: {last_error}")

    def _resolve_model_key(self, override: Optional[str]) -> str:
        """Return a valid model key, defaulting as necessary."""

        if override:
            key = override.lower()
            if key not in self.models:
                raise ValueError(f"Unknown chart vision model '{override}'")
            return key

        env_key = (os.getenv("CHART_VISION_MODEL") or "").lower().strip()
        if env_key and env_key in self.models:
            return env_key

        if env_key:
            logger.warning("CHART_VISION_MODEL '%s' not recognized; falling back to gpt-5-mini", env_key)

        return "gpt-5-mini"

    def _extract_response_text(self, response: Any) -> str:
        """Extract text payload from Responses API output."""
        try:
            outputs = getattr(response, "output", [])
            for item in outputs:
                content_list = item.get("content", [])
                for content in content_list:
                    if content.get("type") in {"output_text", "text"}:
                        return content.get("text", "").strip()
        except Exception as exc:  # pragma: no cover
            logger.warning(f"Failed to extract text from response: {exc}")
        return ""

    def _parse_response(self, text: str) -> Dict[str, Any]:
        """Parse JSON response text and normalize structure."""
        if not text:
            return {"patterns": [], "summary": "No response from model."}

        candidate = text.strip()
        if candidate.startswith("```"):
            candidate = self._strip_code_fence(candidate)

        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            logger.debug("Model returned non-JSON content: %s", candidate[:200])
            return {
                "patterns": [],
                "summary": candidate,
                "raw_response": candidate,
            }

        patterns = data.get("patterns") or []
        normalized = []
        for item in patterns:
            normalized.append(
                {
                    "pattern_id": item.get("pattern_id") or item.get("pattern"),
                    "category": item.get("category"),
                    "bias": item.get("bias") or item.get("signal"),
                    "confidence": item.get("confidence"),
                    "evidence": item.get("evidence") or item.get("notes"),
                    "recommended_action": item.get("recommended_action"),
                    "key_levels": item.get("key_levels", {}),
                    "targets": item.get("targets") or [],
                    "trendline_points": item.get("trendline_points") or item.get("trendline") or item.get("anchors"),
                }
            )

        return {
            "patterns": normalized,
            "summary": data.get("summary"),
            "raw_response": candidate if normalized == [] else None,
        }

    @staticmethod
    def _strip_code_fence(text: str) -> str:
        lines = [line for line in text.splitlines() if not line.strip().startswith("```")]
        return "\n".join(lines).strip()
