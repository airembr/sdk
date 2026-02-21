from __future__ import annotations
from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class LLMConfig:
    provider: Literal["open-router", "open-ai", "anthropic"]
    api_key: str
    model: str
    timeout: float = 30.0
    max_retries: int = 3
    max_tokens: int = 1024