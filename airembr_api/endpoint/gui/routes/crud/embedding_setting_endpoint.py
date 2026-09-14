from fastapi import APIRouter, Depends

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config
from airembr.model.metadata.sys_embedding_setting import EmbeddingSetting
from airembr.system.command.embedding.embedding_setting import (
    get_embedding_setting as get_embedding_setting_cmd,
    save_embedding_setting as save_embedding_setting_cmd,
    delete_embedding_setting as delete_embedding_setting_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer", "maintainer"]))]
)


@router.get("/v2/embedding/{embedding_id}", tags=["v2/ai"], include_in_schema=sys_config.expose_gui_api)
async def get_segment(embedding_id: str):
    return await get_embedding_setting_cmd(embedding_id)


@router.post("/v2/embedding", tags=["v2/ai"], include_in_schema=sys_config.expose_gui_api)
async def save_segment(embedding: EmbeddingSetting):
    await save_embedding_setting_cmd(embedding)


@router.delete("/v2/embedding/{embedding_id}", tags=["v2/ai"], include_in_schema=sys_config.expose_gui_api)
async def delete_segment(embedding_id: str):
    return await delete_embedding_setting_cmd(embedding_id)
