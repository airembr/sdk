from fastapi import APIRouter, Depends

from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config
from airembr.model.metadata.sys_ent_segment import EntitySegment
from airembr.system.command.segment.segment import (
    save_segment as save_segment_cmd,
    get_segment as get_segment_cmd,
    delete_segment as delete_segment_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer", "maintainer"]))]
)


@router.post("/v2/segment", tags=["v2/segment"], include_in_schema=sys_config.expose_gui_api)
async def save_segment(segment: EntitySegment):
    await save_segment_cmd(segment)


@router.get("/v2/segment/{segment_id}", tags=["v2/segment"], include_in_schema=sys_config.expose_gui_api)
async def get_segment(segment_id: str):
    return await get_segment_cmd(segment_id)


# Can  not be /v2/segment/{segment_id} because deply is not refactored
@router.delete("/segment/{segment_id}", tags=["v2/segment"], include_in_schema=sys_config.expose_gui_api)
async def delete_segment(segment_id: str):
    return await delete_segment_cmd(segment_id)
