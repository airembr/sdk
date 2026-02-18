from typing import Optional, Type

import instructor
from pydantic import BaseModel

from airembr.sdk.service.remote.llm.driver.base import BaseProvider


class OpenRouterProvider(BaseProvider):

    async def infer(
            self,
            system_prompt: str,
            user_prompt: str,
            temperature: float,
            structured_output: Optional[Type[BaseModel]] = None,
    ) -> str:
        client = instructor.from_provider(
            f"openrouter/{self._config.model}",
            base_url="https://openrouter.ai/api/v1",
            async_client=True,
            api_key=self._config.api_key,
        )

        return await client.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            extra_body={"provider": {"require_parameters": True}},
            max_retries=self._config.max_retries,
            response_model=structured_output,
            max_tokens=self._config.max_tokens
        )
