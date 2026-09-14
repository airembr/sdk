from typing import Optional

from airembr.system.config.sys_config import sys_config
from airembr.system.config.memory_cache_config import memory_cache_config
from fastapi import APIRouter, Depends, HTTPException
from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions
from airembr.system.command.v1.errors.reshaping_schema_errors import EventReshapingError
from airembr.system.command.v1.list.reshaping_schema.list import (
    get_reshape_schemas_by_event_type as get_reshape_schemas_by_event_type_cmd,
    load_reshape_schemas as load_reshape_schemas_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/event-reshape-schemas/by_type/{event_type}", tags=["reshaping"],
            include_in_schema=sys_config.expose_gui_api,
            response_model=dict)
async def get_reshape_schemas_by_event_type(event_type: str, only_enabled: bool = True):
    try:
        records, total = await get_reshape_schemas_by_event_type_cmd(event_type, only_enabled)
    except EventReshapingError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

    return {
        "total": total,
        "result": records
    }


@router.get("/event-reshape-schema", tags=["reshaping"], include_in_schema=sys_config.expose_gui_api, response_model=dict)
async def load_reshape_schemas(limit: Optional[int] = 100, query: Optional[str] = None):
    records, total = await load_reshape_schemas_cmd(limit, query)
    return {
        "total": total,
        "grouped": {
            "Payload Reshaping": records
        },
        "cache": memory_cache_config.event_reshaping_cache_ttl
    }
