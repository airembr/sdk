from fastapi import APIRouter, Depends

from airembr.system.config.sys_config import sys_config
from airembr.system.command.v1.data.observation.observation import (
    get_observation as get_observation_cmd,
    delete_observation as delete_observation_cmd,
)

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer", "maintainer"]))]
)


@router.get("/v2/observation/{observation_id}", tags=["v2/observation"], include_in_schema=sys_config.expose_gui_api)
async def get_observation(observation_id: str):
    return await get_observation_cmd(observation_id)


@router.delete("/v2/observation/{observation_id}", tags=["v2/observation"], include_in_schema=sys_config.expose_gui_api)
async def delete_observation(observation_id: str):
    await delete_observation_cmd(observation_id)
