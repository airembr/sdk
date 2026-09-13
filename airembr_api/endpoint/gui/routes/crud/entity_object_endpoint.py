from fastapi import APIRouter, Depends

from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config
from airembr.model.entity_object import EntityObject
from airembr.system.command.entity_object.entity_object import (
    save_entity_object as save_entity_object_cmd,
    get_entity_object_payload as get_entity_object_payload_cmd,
    delete_entity_object as delete_entity_object_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer", "maintainer"]))]
)


@router.post("/v2/entity/object", tags=["v2/entity"], include_in_schema=sys_config.expose_gui_api)
async def save_entity_object(entity_object: EntityObject):
    await save_entity_object_cmd(entity_object)


@router.get("/v2/entity/object/{entity_type_id}", tags=["v2/entity"], include_in_schema=sys_config.expose_gui_api)
async def get_entity_object_payload(entity_type_id: str):
    return await get_entity_object_payload_cmd(entity_type_id)


@router.delete("/v2/entity/object/{entity_type_id}", tags=["v2/entity"], include_in_schema=sys_config.expose_gui_api)
async def delete_entity_object(entity_type_id: str):
    return await delete_entity_object_cmd(entity_type_id)
