import asyncio
import os

from asyncio import sleep
from time import time

from srd.config import StarRocksConfig

from airembr_sdk.model.core.instance_link import InstanceLink
from airembr.model.system.entity import Entity
from airembr.model.api.request.observation import Observation, ObservationTimer, StatusEnum, ObservationRelation, \
    Semantic
from airembr.system.process.logging.log_manager import save_logs
from airembr.system.process.logging.log_handler import get_logger
from airembr.system.adapter.bigdata.tenant.tenant_adapter import load_tenant_database_and_context
from airembr.system.adapter.metadata.mysql.service.task_service import background_log
from airembr.model.system.headers import Headers
from airembr.system.adapter.bigdata.big_data_adapter import *
from airembr.model.bigdata.flat_sys_timer import FlatSysTimer
from airembr.model.system.context import ServerContext, Context
from airembr.system.process.logging import extra_info
from airembr.system.process.collection.collector import Collector

logger = get_logger(__file__)


async def _trigger_timers(context: Context):
    result = await bd_timer_adapter.load_active_timers()

    timer_ids = set()

    headers = Headers({
        'x-api-key': 'abc',
        'x-realtime': 'collect,process',
        'x-context': 'production' if context.production else 'test',
        'x-tenant': context.tenant
    })

    for timer in result:

        timer_id = timer.get(FlatSysTimer.ID, None)
        actor_id = timer.get(FlatSysTimer.ACTOR_ID, None)
        object_id = timer.get(FlatSysTimer.OBJECT_ID, None)
        obs_entities = {}

        actor_link = None
        if actor_id:
            actor_instance = f"{timer[FlatSysTimer.ACTOR_TYPE]}#{timer[FlatSysTimer.ACTOR_ID]}"
            actor_link = InstanceLink.create('actor-1')
            obs_entities[actor_link] = {
                "instance": actor_instance
            }

        object_link = None
        if object_id:
            object_instance = f"{timer[FlatSysTimer.OBJECT_TYPE]}#{timer[FlatSysTimer.OBJECT_ID]}"
            object_link = InstanceLink.create('object-1')
            obs_entities[object_link] = {
                "instance": object_instance
            }

        timer_traits = timer.get(FlatSysTimer.TRAITS, {})

        event = timer[FlatSysTimer.EVENT]

        # # Timer does not have entity traits
        observation = Observation(
            id=timer[FlatSysTimer.OBS_ID],
            label=timer[FlatSysTimer.OBS_LABEL],
            text=Semantic(summary=f"Fact timed-out. Fact {event} recorded.", ner=False),
            source=Entity(id=timer[FlatSysTimer.SOURCE_ID]),
            entities=obs_entities,
            observer=actor_link,
            relation=[
                ObservationRelation(
                    observer=actor_link,
                    actor=actor_link,
                    type='timer',
                    label=event,
                    objects=[object_link] if object_link else [],
                    context=[],
                    traits=timer_traits,
                    timer=ObservationTimer(
                        id=timer_id,
                        status=StatusEnum.off,
                        timeout=timer[FlatSysTimer.TIMEOUT],
                        event=event
                    )
                )],
            tags=['system:timer']
        )

        collector = Collector(headers, [observation])
        number_of_observations, dispatch_status = await collector.register_observation()

        print(1,number_of_observations)
        print(2, dispatch_status)

        # Must wait when there is a worker
        timer_ids.add(timer_id)

    if headers.has_no_queue_services():
        await sleep(2)

    return timer_ids


async def main():
    t = time()

    config = StarRocksConfig()

    logger.info(
        f"Config: starrocks_database_uri = {config.starrocks_database_uri} (env: {os.environ.get('STARROCKS_HOST', None)})")

    # Scan database names and produce context
    async for database, context in load_tenant_database_and_context():

        # Make context
        with ServerContext(context):

            async with background_log("Timer tigger", f"Timer in context {context}") as (bts, task_id):
                await bts.task_progress(task_id, 10)
                logger.info(f"Context: {context}, Database: {database}")
                try:
                    triggered_timer_ids = await _trigger_timers(context)
                    number_of_timers = len(triggered_timer_ids)
                    if number_of_timers == 110:
                        continue
                    msg = f"Executed {number_of_timers} active timers in context {context}."
                    logger.info(msg)

                    # Delete old timers
                    await bd_timer_adapter.reset_timers()
                except Exception as e:
                    logger.error(f"Timer error: {str(e)}",
                                 extra=extra_info.build("Timer Worker", error_number='TW-0001'))
                finally:
                    await save_logs()
                    # Await to resolve async push to queue

    await sleep(1)

    logger.info(f"Finished in {time() - t}")


asyncio.run(main())
