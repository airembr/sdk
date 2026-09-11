from fastapi import APIRouter, Depends
from typing import Optional, List

from airembr_api.endpoint.gui.auth.permissions import Permissions

from airembr.system.config.sys_config import sys_config
from airembr.system.command.pill.pill import (
    import_texts as import_texts_cmd,
    count_facts_by_source as count_facts_by_source_cmd,
    count_texts_by_source as count_texts_by_source_cmd,
    export_texts_by_source as export_texts_by_source_cmd,
    export_facts_by_source as export_facts_by_source_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer", "maintainer"]))]
)

@router.post("/v2/texts/import", tags=["v2/pill/export"], include_in_schema=sys_config.expose_gui_api)
async def import_texts(rows: List[dict]):
    return await import_texts_cmd(rows)

@router.get("/v2/facts/source/{source_id}/count", tags=["v2/pill/export"], include_in_schema=sys_config.expose_gui_api)
async def count_facts_by_source(source_id: str):
    return await count_facts_by_source_cmd(source_id)

@router.get("/v2/texts/source/{source_id}/count", tags=["v2/pill/export"],
            include_in_schema=sys_config.expose_gui_api)
async def count_texts_by_source(source_id: str):
    return await count_texts_by_source_cmd(source_id)


@router.get("/v2/texts/source/{source_id}/page/{page}/export", tags=["v2/pill/export"],
            include_in_schema=sys_config.expose_gui_api)
async def export_texts_by_source(source_id: str, page: Optional[int] = None, page_size: Optional[int] = None):
    return await export_texts_by_source_cmd(source_id, page, page_size)

@router.get("/v2/facts/source/{source_id}/page/{page}/export", tags=["v2/pill/export"],
            include_in_schema=sys_config.expose_gui_api)
async def export_facts_by_source(source_id: str, page: Optional[int] = None):
    return await export_facts_by_source_cmd(source_id, page)
