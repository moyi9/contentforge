"""OpenAI-compatible LLM client for ContentForge.

Supports any OpenAI-compatible API provider (OpenAI, DeepSeek, Claude via API,
vLLM, Ollama, etc.) by configuring llm_base_url and llm_api_key.
"""

import json
from typing import Any
from httpx import AsyncClient, Timeout
from app.config import settings


class LLMClient:
    """Unified LLM client that speaks OpenAI chat completions format."""

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        self.model = model or settings.llm_model or "gpt-4o"
        self.api_key = api_key or settings.llm_api_key or ""
        self.base_url = (base_url or settings.llm_base_url or
                         "https://api.openai.com/v1").rstrip("/")
        self._client = AsyncClient(
            timeout=Timeout(60.0),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        response_format: dict | None = None,
    ) -> dict[str, Any]:
        """Send a chat completion request.

        Args:
            messages: List of {"role": "user"/"system"/"assistant", "content": "..."}
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            response_format: Optional {"type": "json_object"} for structured output

        Returns:
            Parsed response dict with keys: content, finish_reason, usage
        """
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            body["response_format"] = response_format

        resp = await self._client.post(f"{self.base_url}/chat/completions", json=body)
        resp.raise_for_status()
        data = resp.json()

        choice = data["choices"][0]
        content = choice["message"]["content"]
        finish_reason = choice.get("finish_reason", "stop")
        usage = data.get("usage", {})

        # If response_format is json_object, parse the content
        if response_format and response_format.get("type") == "json_object":
            try:
                content = json.loads(content)
            except (json.JSONDecodeError, TypeError):
                pass

        return {
            "content": content,
            "finish_reason": finish_reason,
            "usage": usage,
            "model": self.model,
        }

    async def chat_json(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> dict:
        """Send a chat completion with json_object response format."""
        result = await self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        if isinstance(result["content"], str):
            result["content"] = json.loads(result["content"])
        return result

    async def close(self):
        await self._client.aclose()
