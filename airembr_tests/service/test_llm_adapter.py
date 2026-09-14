import asyncio
import json
import unittest
from unittest.mock import patch

import httpx
from pydantic import BaseModel

from airembr.sdk.service.remote.llm.llm_adapter import LLMAdapter


class Answer(BaseModel):
    name: str
    age: int


def _fake_tool_call_response(response_model: type) -> dict:
    """Build a realistic OpenAI-compatible chat completion with a tool-call
    payload, matching the shape instructor's default TOOLS mode expects."""
    return {
        "id": "chatcmpl-fake",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "openai/gpt-4o-mini",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": response_model.__name__,
                        "arguments": json.dumps({"name": "Ada", "age": 30}),
                    },
                }],
            },
            "finish_reason": "tool_calls",
        }],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }


class TestLlmAdapterOpenRouter(unittest.TestCase):
    """Exercises the real instructor -> openai -> jiter -> instructor chain,
    mocked only at the httpx transport layer, to catch dependency-version
    regressions that a construction-only smoke test would miss."""

    def test_infer_returns_structured_output_via_openrouter(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json=_fake_tool_call_response(Answer))

        orig_async_client_init = httpx.AsyncClient.__init__

        def patched_init(self, *args, **kwargs):
            kwargs['transport'] = httpx.MockTransport(handler)
            return orig_async_client_init(self, *args, **kwargs)

        adapter = LLMAdapter(provider="open-router", api_key="sk-or-v1-fake", model="openai/gpt-4o-mini")

        with patch.object(httpx.AsyncClient, '__init__', patched_init):
            result = asyncio.run(adapter.infer("system prompt", "hi", structured_output=Answer))

        self.assertIsInstance(result, Answer)
        self.assertEqual(result.name, "Ada")
        self.assertEqual(result.age, 30)


if __name__ == '__main__':
    unittest.main()
