import asyncio

from airembr.sdk.ai.prompt.time_span_prompt import system_time_span_prompt, user_time_span_prompt, ExtractedTimeSpan
from airembr.sdk.service.remote.llm.llm_adapter import LLMAdapter
from airembr.sdk.ai.config import LLM_PROVIDER, LLM_PROVIDER_API_KEY, LLM_TIME_EXTRACTION_MODEL

adapter = LLMAdapter(
    provider=LLM_PROVIDER,
    api_key=LLM_PROVIDER_API_KEY,
    model=LLM_TIME_EXTRACTION_MODEL
)

async def extract_timespan(text):
    result = await adapter.infer(
        system_prompt=system_time_span_prompt,
        user_prompt=user_time_span_prompt(text),
        structured_output=ExtractedTimeSpan
    )
    print(result)


asyncio.run(extract_timespan("czy wczoraj dostałem paczke"))