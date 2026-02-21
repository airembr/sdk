import logging
from abc import ABC, abstractmethod
from typing import Type, Optional

from pydantic import BaseModel

from airembr.sdk.service.remote.llm.llm_config import LLMConfig


class BaseProvider(ABC):
    def __init__(self, config: LLMConfig, logger: logging.Logger):
        self._config = config
        self._logger = logger

    @abstractmethod
    async def infer(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        structured_output: Optional[Type[BaseModel]] = None,
    ) -> BaseModel:
        ...
