from typing import Optional, Any, Sequence

from openai import AsyncOpenAI
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic_ai.settings import ModelSettings

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider


class LlmAdapter(BaseModel):
    service_provider: str
    api_key: Optional[str] = None
    api_url: Optional[str] = None

    def model(self, model_name: str) -> 'LlmModel':
        return LlmModel(adapter=self, model_name=model_name)


class LlmModel(BaseModel):
    adapter: LlmAdapter
    model_name: str

    async def prompt(self, user_prompt: str, system_prompt: str | Sequence[str] = (), output_format: Optional[Any] = None,
                     temperature: Optional[float] = None):
        if temperature:
            settings = ModelSettings(temperature=temperature)
        else:
            settings = None

        if self.adapter.service_provider == "open-router":
            model = OpenRouterModel(
                self.model_name,
                settings=settings,
                # This is for open router
                provider=OpenRouterProvider(
                    api_key=self.adapter.api_key
                ),
            )
        else:
            client = AsyncOpenAI(max_retries=3, base_url=self.adapter.api_url, api_key=self.adapter.api_key)
            model = OpenAIChatModel(
                self.model_name,
                settings=settings,
                provider=OpenAIProvider(openai_client=client)
            )

        if output_format is None:
            agent = Agent(
                model,
                system_prompt=system_prompt
            )
        else:
            agent = Agent(
                model,
                output_type=output_format,
                system_prompt=system_prompt
            )

        return await agent.run(user_prompt)
