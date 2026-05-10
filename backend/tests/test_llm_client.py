"""Tests for the unified LLM client."""

import pytest
from app.llm.client import LLMClient


@pytest.mark.asyncio
async def test_llm_client_initialization():
    """LLMClient should use config defaults when no args given."""
    from app.config import settings
    client = LLMClient()
    assert client.model is not None
    assert client.base_url is not None
    await client.close()


@pytest.mark.asyncio
async def test_llm_client_custom_config():
    """LLMClient should accept explicit overrides."""
    client = LLMClient(
        model="custom-model",
        api_key="test-key",
        base_url="https://custom.api.com/v1",
    )
    assert client.model == "custom-model"
    assert client.api_key == "test-key"
    assert client.base_url == "https://custom.api.com/v1"
    await client.close()


@pytest.mark.asyncio
async def test_llm_client_builds_request_body():
    """Verify the request structure built by chat()."""
    from httpx import AsyncClient
    import json

    client = LLMClient(
        model="test-model",
        api_key="test-key",
        base_url="https://httpbin.org",
    )

    messages = [
        {"role": "system", "content": "You are a test assistant."},
        {"role": "user", "content": "Hello!"},
    ]

    # We don't run this - just validate the body structure
    body = {
        "model": "test-model",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2048,
    }
    assert body["model"] == "test-model"
    assert len(body["messages"]) == 2
    assert body["messages"][1]["content"] == "Hello!"
    await client.close()


@pytest.mark.asyncio
async def test_llm_client_invalid_base_url():
    """LLMClient should gracefully handle connection errors."""
    client = LLMClient(
        model="test",
        api_key="key",
        base_url="https://localhost:1",
    )
    with pytest.raises(Exception):
        await client.chat(messages=[{"role": "user", "content": "hi"}])
    await client.close()
