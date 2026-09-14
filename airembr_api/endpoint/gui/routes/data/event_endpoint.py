from fastapi import APIRouter, Depends
from typing import Optional

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions
from airembr.model.api.request.time_range import DatetimeRangePayload

from airembr.system.config.sys_config import sys_config
from airembr.system.command.v1.data.event.event import (
    load_event_by_query as load_event_by_query_cmd,
    get_event_histogram as get_event_histogram_cmd,
    get_events_for_actor_entity as get_events_for_actor_entity_cmd,
    get_events_for_object_entity as get_events_for_object_entity_cmd,
    get_event_type_data_schema as get_event_type_data_schema_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer", "maintainer"]))]
)


@router.post("/v2/events/list", tags=["v2/data"], include_in_schema=sys_config.expose_gui_api)
@router.post("/v2/events/list/page/{page}", tags=["v2/data"], include_in_schema=sys_config.expose_gui_api)
async def load_event_by_query(query: DatetimeRangePayload, page: Optional[int] = None, shorten: bool = True):
    return await load_event_by_query_cmd(query, page, shorten)


@router.post("/v2/events/histogram", tags=["data"], include_in_schema=sys_config.expose_gui_api)
async def event_histogram(query: DatetimeRangePayload):
    return await get_event_histogram_cmd(query)


@router.get("/v2/actor/{entity_pk}/events/", tags=["v2/event"], include_in_schema=sys_config.expose_gui_api)
async def get_events_for_actor_entity(entity_pk: str, limit: int = 24):
    return await get_events_for_actor_entity_cmd(entity_pk, limit)


@router.get("/v2/object/{entity_pk}/events/", tags=["v2/event"], include_in_schema=sys_config.expose_gui_api)
async def get_events_for_object_entity(entity_pk: str, limit: int = 24):
    return await get_events_for_object_entity_cmd(entity_pk, limit)


@router.get("/event/type/{event_type}/schema/{entity_name}", tags=["event"],
            include_in_schema=sys_config.expose_gui_api)
async def get_event_type_data_schema(event_type: str, entity_name: str):
    """Gets pre-defined event type data schema"""
    return await get_event_type_data_schema_cmd(event_type, entity_name)
