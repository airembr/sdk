from typing import Optional

from fastapi import APIRouter, Depends

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config
from airembr.system.command.v1.list.entity_object.list import (
    get_entity_observations as get_entity_observations_cmd,
    list_entity_objects as list_entity_objects_cmd,
    get_entity_texts as get_entity_texts_cmd,
    list_entity_tables as list_entity_tables_cmd,
    get_entity_history as get_entity_history_cmd,
    load_events_by_data_hash as load_events_by_data_hash_cmd,
    get_entity_object_current_state as get_entity_object_current_state_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer", "maintainer"]))]
)


@router.get("/v2/entity/observations", tags=["v2/entity"], include_in_schema=sys_config.expose_gui_api)
async def get_entity_observations(entity_pk: str):
    return await get_entity_observations_cmd(entity_pk)


@router.get("/v2/entity/objects/list", tags=["v2/entity"], include_in_schema=sys_config.expose_gui_api)
async def list_entity_objects(query: Optional[str] = None, start: int = 0, limit: int = 100):
    records, total = await list_entity_objects_cmd(query, start, limit)
    return {
        "total": total,
        "grouped": {
            "Entities": records
        }
    }


@router.get("/v2/entity/texts", tags=["v2/entity"], include_in_schema=sys_config.expose_gui_api)
async def get_entity_texts(entity_pk: str):
    return await get_entity_texts_cmd(entity_pk)


@router.get("/v2/entity/tables", tags=["v2/entity"], include_in_schema=sys_config.expose_gui_api)
async def list_entity_tables():
    return await list_entity_tables_cmd()


@router.get("/v2/entity/{entity_id}/history", tags=["v2/entity"], include_in_schema=sys_config.expose_gui_api)
async def get_entity_history(entity_id: str):
    return await get_entity_history_cmd(entity_id)


@router.get("/v2/entity/history/use/{data_hash}", tags=["v2/entity"], include_in_schema=sys_config.expose_gui_api)
async def load_events_by_data_hash(data_hash: str):
    return await load_events_by_data_hash_cmd(data_hash)


@router.get("/v2/entity/{entity_pk}/traits/state", tags=["v2/entity"], include_in_schema=sys_config.expose_gui_api)
async def get_entity_object_current_state(entity_pk: str, observer_pk: Optional[str] = None):
    return await get_entity_object_current_state_cmd(entity_pk, observer_pk)
