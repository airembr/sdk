from typing import Optional
from fastapi import APIRouter, Depends

from airembr.sdk.common.map_to_named_entity import map_to_named_entity
from airembr_api.service.grouping import get_result_dict

from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config
from airembr.model.metadata.sys_ent_segment import EntitySegment
from airembr.system.command.segment.segment import (
    list_segments as list_segments_cmd,
    list_segments_meta as list_segments_meta_cmd,
    save_segment as save_segment_cmd,
    get_segment as get_segment_cmd,
    delete_segment as delete_segment_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer", "maintainer"]))]
)


@router.get("/v2/segments", tags=["v2/segment"], include_in_schema=sys_config.expose_gui_api)
async def list_segments(query: Optional[str] = None, start: int = 0, limit: int = 100):
    records, total = await list_segments_cmd(query, start, limit)
    return {
        "total": total,
        "grouped": {
            "Segments": records
        }
    }


@router.get("/v2/segments/meta", tags=["v2/segment"], include_in_schema=sys_config.expose_gui_api)
async def list_segments_meta(query: Optional[str] = None, start: int = 0, limit: int = 100):
    records = await list_segments_meta_cmd(query, start, limit)
    return get_result_dict(records, map_to_named_entity, lambda table_row: table_row.enabled == True)


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
