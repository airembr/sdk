from fastapi import APIRouter, Depends

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config
from airembr.model.metadata.sys_embedding_setting import EmbeddingSetting
from airembr.system.command.v1.meta.embedding_setting.embedding_setting import (
    get_embedding_setting as get_embedding_setting_cmd,
    save_embedding_setting as save_embedding_setting_cmd,
    delete_embedding_setting as delete_embedding_setting_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer", "maintainer"]))]
)


@router.get("/v1/embedding-setting/{embedding_id}", tags=["v2/ai"], include_in_schema=sys_config.expose_gui_api)
async def get_embedding_setting_by_id(embedding_id: str):
    return await get_embedding_setting_cmd(embedding_id)


@router.post("/v1/embedding-setting", tags=["v2/ai"], include_in_schema=sys_config.expose_gui_api)
async def save_embedding_setting(embedding: EmbeddingSetting):
    await save_embedding_setting_cmd(embedding)


@router.delete("/v1/embedding-setting/{embedding_id}", tags=["v2/ai"], include_in_schema=sys_config.expose_gui_api)
async def delete_embedding_setting_by_id(embedding_id: str):
    return await delete_embedding_setting_cmd(embedding_id)
