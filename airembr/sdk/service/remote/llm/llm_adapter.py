import logging
from typing import Literal, Optional, Type

from pydantic import BaseModel

from airembr.sdk.service.remote.llm.driver.anthropic import AnthropicProvider
from airembr.sdk.service.remote.llm.driver.base import BaseProvider
from airembr.sdk.service.remote.llm.driver.google import GoogleAIProvider
from airembr.sdk.service.remote.llm.driver.open_ai import OpenAIProvider
from airembr.sdk.service.remote.llm.driver.open_router import OpenRouterProvider
from airembr.sdk.service.remote.llm.exception import ProviderNotSupportedError
from airembr.sdk.service.remote.llm.llm_config import LLMConfig


class LLMAdapter:
    """
    Unified LLM adapter hiding provider-specific implementations.
    """

    def __init__(
            self,
            provider: Literal["open-router", "open-ai", "anthropic"],
            api_key: str,
            model: str,
            timeout: float = 30.0,
            max_retries: int = 3,
            max_tokens: int = 1024,
            logger: Optional[logging.Logger] = None,
    ) -> None:
        self._config = LLMConfig(
            provider=provider,
            api_key=api_key,
            model=model,
            timeout=timeout,
            max_retries=max_retries,
            max_tokens=max_tokens,
        )

        self._logger = logger or logging.getLogger(__name__)
        self._provider = self._initialize_provider()

    def _initialize_provider(self) -> BaseProvider:
        match self._config.provider:
            case "open-ai":
                return OpenAIProvider(self._config, self._logger)
            case "open-router":
                return OpenRouterProvider(self._config, self._logger)
            case "anthropic":
                return AnthropicProvider(self._config, self._logger)
            case "google":
                return GoogleAIProvider(self._config, self._logger)
            case _:
                raise ProviderNotSupportedError(
                    f"Provider '{self._config.provider}' is not supported."
                )

    # --------------------------------------------------------
    # Public Inference API
    # --------------------------------------------------------

    async def infer(
            self,
            system_prompt: str,
            user_prompt: str,
            temperature: float = 0.7,
            structured_output: Optional[Type[BaseModel]] = None,
    ) -> BaseModel:

        return await self._provider.infer(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            structured_output=structured_output,
        )
