from durable_dot_dict.dotdict import DotDict

from time import time
from typing import List, Optional

from pararun_adapter import queue_type
from pararun.consumer.batcher import BulkedResult
from pararun.model.batcher import BatcherConfig
from pararun.model.transport_context import TransportContext
from pararun.publisher.deferer import deferred_execution

from airembr.sdk.common.date import now_in_utc
from airembr.core.data.chunker import chunk_generator
from airembr.model.system.job_tags import ENTITY_PROPERTY_TAG
from airembr.model.system.context import ServerContext, Context
from airembr.model.bigdata.flat_ent_state import FlatEntityState
from airembr.system.logging.log_handler import get_logger
from airembr.system.adapter.bigdata.general.utils.mapping import entity_property, sys_ent_property_state
from airembr.system.process.collection.deduplication.entity_prop_dedup import PropertyDeduper
from airembr.system.adapter.bigdata.tool.column_mapper import map_to_table_columns
from airembr.system.adapter.bigdata.big_data_adapter import *
from airembr.system.adapter.queue.queue_adapter import queue_adapter


logger = get_logger(__name__)
_ent_property_mapping = entity_property()
_ent_property_state_mapping = sys_ent_property_state()
dedup = PropertyDeduper()


def _convert_to_rows(merged_entities):
    for entity in merged_entities['entities']:
        row = {
            FlatEntityState.TS: now_in_utc(),
            FlatEntityState.PK: entity['entityPk'],
            FlatEntityState.ID: entity['entityId'],
            FlatEntityState.TYPE: entity['entityType']}

        traits = {}
        for property, value in entity['properties'].items():
            traits[property] = value['value']
        row[FlatEntityState.TRAITS] = traits
        yield row


async def save_entity_properties(property_rows):
    _property_column_rows = list(map_to_table_columns(property_rows,
                                                      mapping=_ent_property_mapping))

    return await bd_event_adapter.adapter.stream(_property_column_rows,
                                                 _ent_property_mapping)


async def _save_entity_property_states(property_rows):
    _property_column_rows = list(
        map_to_table_columns(property_rows,
                             mapping=_ent_property_state_mapping)
    )

    return await bd_event_adapter.adapter.stream(_property_column_rows,
                                                 _ent_property_state_mapping)


async def _save_entity_property_states_batch(transport_context: TransportContext,
                                             batch: List[dict],  # Is a batch
                                             metadata: Optional[dict] = None):
    if metadata:
        for trace_id in set(metadata):
            logger.q_info(f"Acquired property states message [{trace_id}] from bulk [{transport_context.trace_id}]")

    # Start
    with ServerContext(Context(**transport_context.as_context())):
        start_time = time()

        # Saves properties
        status, total_rows, saved_rows, message = await _save_entity_property_states(batch)

        end_time = time()
        logger.stat(
            f"Entity Property States: Saved {saved_rows}, "
            f"Saving={end_time - start_time}, Context={transport_context.tenant}/{transport_context.production}")


async def _save_entity_property_history_batch(transport_context: TransportContext,
                                              batch: List[dict],
                                              metadata: Optional[dict] = None):
    # Make batch unique ad count duplicates
    property_rows = batch

    if metadata:
        for trace_id in set(metadata):
            logger.q_info(f"Acquired properties message [{trace_id}] from bulk [{transport_context.trace_id}]")

    # Start
    with ServerContext(Context(**transport_context.as_context())):
        start_time = time()
        # Saves properties
        status, total_rows, saved_rows, message = await save_entity_properties(property_rows)

        end_time = time()
        logger.stat(
            f"Entity Property History: Saved {saved_rows}, "
            f"Saving={end_time - start_time}, Context={transport_context.tenant}/{transport_context.production}")


async def _save_property_changes_job(transport_context: TransportContext, property_rows: List[DotDict]):
    max_prop_size = 1000
    props_size = len(property_rows)
    if props_size > max_prop_size:
        chunk_size: int = (props_size // max_prop_size) + 1
        logger.dev_info(
            f"Splitting entity properties in queue into {chunk_size} batches of {max_prop_size}. This is protection against too big queue payloads.")
        for chunked_props in chunk_generator(property_rows, max_prop_size, True):
            chunked_props = list(chunked_props)
            await _save_entity_property_history_batch(
                transport_context,
                batch=chunked_props
            )
        return None
    else:
        return await _save_entity_property_history_batch(
            transport_context,
            batch=property_rows
        )


async def _save_property_states_job(transport_context: TransportContext, property_rows: List[DotDict]):
    # Saves property state
    max_prop_size = 1000
    props_size = len(property_rows)
    if props_size > max_prop_size:
        chunk_size: int = (props_size // max_prop_size) + 1
        logger.dev_info(
            f"Splitting entity property states in queue into {chunk_size} batches of {max_prop_size}. This is protection against too big queue payloads.")
        for chunked_props in chunk_generator(property_rows, max_prop_size, True):
            chunked_props = list(chunked_props)
            await _save_entity_property_states_batch(
                transport_context,
                batch=chunked_props
            )
        return None
    else:
        return await _save_entity_property_states_batch(
            transport_context,
            batch=property_rows
        )


async def save_properties_batch(transport_context: TransportContext,
                                batch: List[dict],
                                metadata: Optional[dict] = None):
    # Saves traits changes
    await _save_property_changes_job(transport_context, batch)

    # Saves traits states
    # property_row_without_rel = [item for item in batch if not item.get(FlatEntityProperty._IS_RELATION, False)]
    await _save_property_states_job(transport_context, batch)


async def save_entity_properties_job(transport_context: TransportContext, property_rows: List[DotDict],
                                     queue: bool = True):
    return BulkedResult(dedup.process(property_rows))


async def entity_properties_worker(transport_context: TransportContext, property_rows: List[DotDict]):
    min_queue_size = 1
    with deferred_execution() as defer:
        return await defer(save_entity_properties_job)(property_rows).push(
            ENTITY_PROPERTY_TAG,
            transport_context,
            batcher=BatcherConfig(
                func=save_properties_batch,
                min_size=min_queue_size,
                max_size=1000,
                timeout=30
            ),
            adapter=queue_adapter(queue_type.ENTITY_MERGING)
        )