from typing import Optional

from fastapi import APIRouter, Depends

from airembr.model.api.request.time_range import DatetimeRangePayload
from airembr.system.config.sys_config import sys_config
from airembr.system.command.observation.observation import (
    get_observation as get_observation_cmd,
    get_observation_facts as get_observation_facts_cmd,
    delete_observation as delete_observation_cmd,
    get_observers_from_facts as get_observers_from_facts_cmd,
    load_observations as load_observations_cmd,
    load_observations_by_query as load_observations_by_query_cmd,
    get_observations_histogram as get_observations_histogram_cmd,
)

from airembr_api.endpoint.gui.auth.permissions import Permissions

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer", "maintainer"]))]
)


@router.get("/v2/observation/{observation_id}", tags=["v2/observation"], include_in_schema=sys_config.expose_gui_api)
async def get_observation(observation_id: str):
    return await get_observation_cmd(observation_id)


@router.get("/v2/observation/{observation_id}/facts/", tags=["v2/observation"],
            include_in_schema=sys_config.expose_gui_api)
async def get_observation_facts(observation_id: str, start: Optional[int] = 0, limit: Optional[int] = 500):
    return await get_observation_facts_cmd(observation_id, start, limit)


@router.delete("/v2/observation/{observation_id}", tags=["v2/observation"], include_in_schema=sys_config.expose_gui_api)
async def delete_observation(observation_id: str):
    await delete_observation_cmd(observation_id)


@router.get("/v2/observers", tags=["v2/observation"],
            include_in_schema=sys_config.expose_gui_api)
async def get_observers_from_facts():
    return await get_observers_from_facts_cmd()


@router.get("/v2/observations", tags=["v2/observation"],
            include_in_schema=sys_config.expose_gui_api)
async def load_observations():
    return await load_observations_cmd()


@router.post("/v2/observations/list/page/{page}", tags=["v2/data"], include_in_schema=sys_config.expose_gui_api)
async def load_observations_by_query(query: DatetimeRangePayload, page: Optional[int] = None):
    return await load_observations_by_query_cmd(query, page)

@router.post("/v2/observations/histogram", tags=["data"], include_in_schema=sys_config.expose_gui_api)
async def event_histogram(query: DatetimeRangePayload):
    return await get_observations_histogram_cmd(query)
