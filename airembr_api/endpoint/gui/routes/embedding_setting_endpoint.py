from typing import Optional
from fastapi import APIRouter, Depends

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config
from airembr.system.command.embedding.embedding_setting import (
    list_embedding_settings as list_embedding_settings_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer", "maintainer"]))]
)


@router.get("/v2/embeddings", tags=["v2/ai"], include_in_schema=sys_config.expose_gui_api)
async def list_segments(query: Optional[str] = None, start: int = 0, limit: int = 100):
    records, total = await list_embedding_settings_cmd(query, start, limit)
    return {
        "total": total,
        "grouped": {
            "Embeddings": records
        }
    }
