from time import time

import asyncio
from uuid import uuid4

from typing import Optional
from airembr.sdk.ai.prompt.event_extration_prompt import event_extraction_system_prompt, event_extraction_user_prompt, \
    ExtractedEvents
from airembr.sdk.ai.prompt.summary_extration_prompt import summary_extraction_system_prompt, \
    summary_extraction_user_prompt, ExtractedSummary
from airembr.system.adapter.bigdata.general.utils.mapping import sys_text_mapping, sys_text_vector_mapping
from airembr.system.process.logging.log_handler import get_logger
from airembr.sdk.service.remote.llm.llm_adapter import LLMAdapter
from airembr.sdk.ai.config import LLM_PROVIDER, LLM_PROVIDER_API_KEY, LLM_ENTITY_EXTRACTION_MODEL, \
    SECOND_LLM_ENTITY_EXTRACTION_MODEL
from airembr.sdk.ai.prompt.entity_extration_prompt import ExtractedEntity, \
    ExtractedEntities, entity_extraction_system_prompt, \
    entity_extraction_user_prompt
from airembr.system.adapter.bigdata.big_data_adapter import bd_text_adapter
from airembr_sdk.client.airembr_chat import AiRembrChatClient, entity
from airembr.model.api.request.observation import EntityIdentification
from airembr_sdk.model.interface.i_observation import IEntityIdentification

logger = get_logger(__name__)
_sys_text_mapping = sys_text_mapping()
_sys_text_vector_mapping = sys_text_vector_mapping()

BULK_SIZE = 500

adapter = LLMAdapter(
    provider=LLM_PROVIDER,
    api_key=LLM_PROVIDER_API_KEY,
    model=LLM_ENTITY_EXTRACTION_MODEL
)

second_adapter = LLMAdapter(
    provider=LLM_PROVIDER,
    api_key=LLM_PROVIDER_API_KEY,
    model=SECOND_LLM_ENTITY_EXTRACTION_MODEL
)

client = AiRembrChatClient(api="http://localhost:4002")


def _get_global_identification(entity: ExtractedEntity) -> Optional[EntityIdentification]:
    entity_type = entity.get_type()
    if entity_type in ['person', 'organization']:
        return EntityIdentification(properties=['email'])
    return None


async def extract_entities(context):
    count = await bd_text_adapter.count_texts_to_ner()
    logger.info(f"There are {count} texts to extract entities from...")
    session_id = str(uuid4())
    data = await bd_text_adapter.load_texts_to_ner()
    for row in data:
        try:
            text_id = row['id']
            text = row['text_string']
            observation_id = row['observation_id'] or str(uuid4())

            if len(text) < 10:
                continue

            t = time()
            events, summary, entities = await asyncio.gather(
                adapter.infer(
                    system_prompt=event_extraction_system_prompt(),
                    user_prompt=event_extraction_user_prompt(text),
                    structured_output=ExtractedEvents
                ),
                adapter.infer(
                    system_prompt=summary_extraction_system_prompt(),
                    user_prompt=summary_extraction_user_prompt(text),
                    structured_output=ExtractedSummary
                ),
                adapter.infer(
                    system_prompt=entity_extraction_system_prompt(),
                    user_prompt=entity_extraction_user_prompt(text),
                    structured_output=ExtractedEntities
                ),
            )
            logger.info(f"Extracted entities in {time() - t} seconds")

            # Define entities
            _entities = set()

            # First get the fact entities
            for _event in events.events:
                traits = {
                    '$type': _event.type,
                    '$summary': _event.fact,
                }

                if _event.started_at:
                    traits['started_at'] = str(_event.started_at)

                if _event.ended_at:
                    traits['ended_at'] = str(_event.ended_at)

                _ent = entity(
                    'fact',
                    traits=traits,
                    id=str(uuid4())  # Must have id otherwise will no be saved
                )
                _entities.add(_ent)

            for _entity in entities.yield_entities():
                idents = _entity._get_global_identification()
                if idents:
                    identification, strict = idents
                    identification = IEntityIdentification(properties=identification, strict=strict)
                else:
                    identification = None

                entity_id = _entity.get_entity_id()

                traits = _entity.traits
                if '$id' in traits:
                    del traits['$id']

                # Fix traits
                for key in ['name', 'label', 'type']:
                    if key in traits:
                        traits[f'${key}'] = traits[key].strip()
                        del traits[key]

                _ent = entity(
                    _entity.get_type(),
                    traits=traits,
                    identification=identification,
                    id=entity_id  # Must have id otherwise will no be saved
                )
                _entities.add(_ent)

            observer = entity('system', traits={"name": "Airembr"}, id="airembr")
            _entities.add(observer)

            source_id = "test1"

            # Define observation
            observation = (
                client.
                observation(
                    id=observation_id,
                    source_id=source_id,
                    session_id=session_id,
                    description=summary.summary,
                    tags=summary.keywords,
                    observer=observer
                ).context(_entities)
                # Add timestamp from fact
            )

            # print(0, observation_id)
            print(observation.remember(
                realtime="collect,store,store-observation,destination,logs",
                bridge="imap,rest,ical"
            )
            )
            await bd_text_adapter.update_required_ner_texts(text_id, LLM_ENTITY_EXTRACTION_MODEL)
        except Exception as e:
            logger.error(e)
