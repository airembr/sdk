from typing import Type, Optional

import instructor
from pydantic import BaseModel
from airembr.sdk.service.remote.llm.driver.base import BaseProvider


class AnthropicProvider(BaseProvider):

    async def infer(
            self,
            system_prompt: str,
            user_prompt: str,
            temperature: float,
            structured_output: Optional[Type[BaseModel]] = None,
    ) -> str:
        async_client = instructor.from_provider(
            f"anthropic/{self._config.model}",
            async_client=True,
            mode=instructor.Mode.TOOLS,
            api_key=self._config.api_key,
        )

        return await async_client.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            response_model=structured_output,
            max_retries=self._config.max_retries,
            max_tokens=self._config.max_tokens
        )
