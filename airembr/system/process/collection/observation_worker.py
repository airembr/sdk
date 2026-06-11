from time import time
from typing import Optional, List

from airembr.core.hash.hash import md5
from pararun_adapter import queue_type
from pararun.consumer.batcher import BulkedResult
from pararun.model.batcher import BatcherConfig
from pararun.model.transport_context import TransportContext, RECORDS
from pararun.publisher.deferer import deferred_execution

from airembr_sdk.core.date import now_in_utc
from airembr.model.bigdata.flat_obs import FlatObs
from airembr.model.system.context import get_context, ServerContext, Context
from airembr.model.system.transport_payload import ObsTransportPayload
from airembr.system.process.logging.log_handler import get_logger, log_handler
from airembr.system.adapter.queue.queue_adapter import queue_adapter
from airembr.model.system.job_tags import OBSERVATION_STORAGE_TAG
from airembr.system.adapter.bigdata.general.utils.mapping import sys_obs_mapping
from airembr.system.adapter.bigdata.big_data_adapter import *

logger = get_logger(__name__)

async def _save_observations(transport_context, observation_batch: List[dict]):

    if observation_batch:
        _sys_obs_mapping = sys_obs_mapping()
        with ServerContext(Context(**transport_context.as_context())) as server:
            start = time()
            now = now_in_utc()
            # ObsTransportPayload has the same schema as sys_obs table
            _ts = _sys_obs_mapping | FlatObs.TS
            _metadata_time_insert = _sys_obs_mapping | FlatObs.METADATA_TIME_INSERT
            _metadata_time_create = _sys_obs_mapping | FlatObs.METADATA_TIME_CREATE
            _summary_id = _sys_obs_mapping | FlatObs.SUMMARY_ID
            _description_id = _sys_obs_mapping | FlatObs.DESCRIPTION_ID

            for item in observation_batch:  # ObsTransportPayload has the same schema as sys_obs table

                if not isinstance(item, dict):
                    raise ValueError(
                        f"Incorrect payload {item}. Expected dict in schema of ObsTransportPayload type, got `{type(item)}`.")

                item[_ts] = now

                summary: Optional[str] = item.get("summary", None)
                if summary is not None:
                    item[_summary_id] = md5(summary)

                description: Optional[str] = item.get("description", None)
                if description is not None:
                    item[_description_id] = md5(description)

                item[_metadata_time_insert] = item[_metadata_time_insert] if item.get(_metadata_time_insert, None) is not None else now
                item[_metadata_time_create] = item[_metadata_time_create] if item.get(_metadata_time_create, None) is not None else now

            # Save
            status, total_rows, saved_rows, message = await bd_event_adapter.adapter.stream(observation_batch,
                                                                                            _sys_obs_mapping)

            end_time = time()
            logger.stat(
                f"Observations: Saved {saved_rows}, "
                f"Time={end_time - start}, "
                f"Context={server.context.tenant}/{server.context.production}")


async def save_obs_in_queue(transport_context: TransportContext,
                            batch: List[dict],  # unserialized ObsTransportPayload is dict
                            metadata: Optional[List[dict]] = None,
                            queue=True):
    await _save_observations(transport_context, batch)


def save_observation_in_queue(context: TransportContext,
                            obs_transport_payload_list: List[ObsTransportPayload]):
        # Storage payload after deserialization lose its types, all are dict
        logger.debug(f"Accepted for batching payload with {len(obs_transport_payload_list)} observations.")
        return BulkedResult(obs_transport_payload_list)  # we need one by one


async def obs_storage_worker(obs_transport_payload_list: List[ObsTransportPayload]):
    if obs_transport_payload_list:
        with deferred_execution() as defer:
            status = await defer(save_observation_in_queue)(obs_transport_payload_list).push(
                OBSERVATION_STORAGE_TAG,
                TransportContext.build(get_context(), params={RECORDS: len(obs_transport_payload_list)}),
                batcher=BatcherConfig(
                    func=save_obs_in_queue,
                    min_size=200,
                    max_size=10000,
                    timeout=3
                ),
                adapter=queue_adapter(queue_type.STORAGE_OBSERVATION)
            )

            if status.logs:
                log_handler.add(status.logs)

            if status.error:
                raise status.error
