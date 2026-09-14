from fastapi import APIRouter, Depends

from airembr.system.config.sys_config import sys_config
from airembr.system.config.memory_cache_config import memory_cache_config
from airembr.system.command.event_validation.validator import (
    load_validators as load_validators_cmd,
)

from airembr_api.endpoint.gui.v1.auth.permissions import Permissions

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.get("/v2/event-configs", tags=["/v2/event"], include_in_schema=sys_config.expose_gui_api,
            response_model=dict)
# @router.get("/event-validator/list", tags=["validation"], include_in_schema=sys_config.expose_gui_api,
#             response_model=dict)
async def load_validators(limit: int = 100, query: str = None):
    validators, total = await load_validators_cmd(limit, query)

    return {
        "total": total,
        "grouped": {
            "Payload Validation": validators
        },
        "cache": memory_cache_config.event_validation_cache_ttl
    }
