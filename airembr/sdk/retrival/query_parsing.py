from typing import List

from airembr.sdk.ai.prompt.entity_extration_prompt import system_prompt, user_prompt, ExtractedEntities, ExtractedEntity
from airembr.sdk.ai.config import LLM_PROVIDER, LLM_PROVIDER_API_KEY, LLM_ENTITY_EXTRACTION_MODEL
from airembr.model.system.meta_language.meta_lang_model import MetaLangEntity
from airembr.sdk.service.remote.llm.llm_adapter import LLMAdapter

adapter = LLMAdapter(
    provider=LLM_PROVIDER,
    api_key=LLM_PROVIDER_API_KEY,
    model=LLM_ENTITY_EXTRACTION_MODEL
)

def _convert_entities(entities: List[ExtractedEntity]) -> List[MetaLangEntity]:
    result = []

    for e in entities:
        print(e)
        properties = [
            (k, v)
            for k, v in (e.traits or {}).items()
            if k not in ["$description"]  # Skip descriptions
        ]
        result.append(
            MetaLangEntity(
                type=e.type.lower(),  # optional normalization
                properties=properties,
                negation=False
            )
        )

    return result

async def parse_semantic_query(text):
    _system_prompt = system_prompt(False, False)
    _user_prompt = user_prompt(text)

    result = await adapter.infer(
        system_prompt=_system_prompt,
        user_prompt=_user_prompt,
        structured_output=ExtractedEntities  # SummarizedExtractedEntities
    )

    return _convert_entities(result.entities)