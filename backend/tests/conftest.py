"""Mock LLM client for deterministic tests."""


class MockLLMClient:
    """Returns pre-configured JSON responses without network calls."""

    def __init__(self, json_response: dict | None = None):
        self._response = json_response

    def set_response(self, data: dict):
        self._response = data

    async def chat(self, messages=None, temperature=0.7, max_tokens=2048,
                   response_format=None):
        content = self._response or {}
        if response_format and response_format.get("type") == "json_object":
            pass  # already a dict
        return {
            "content": content,
            "finish_reason": "stop",
            "usage": {"total_tokens": 100},
            "model": "mock",
        }

    async def chat_json(self, messages=None, temperature=0.3, max_tokens=4096):
        return {
            "content": self._response or {},
            "finish_reason": "stop",
            "usage": {"total_tokens": 100},
            "model": "mock",
        }

    async def close(self):
        pass
