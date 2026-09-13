from fastapi import APIRouter, Depends

from airembr.system.process.logging.log_handler import get_logger
from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config
from airembr.system.command.canonical.entities import (
    list_canonical_entities as list_canonical_entities_cmd,
)
from airembr.system.command.canonical.properties import (
    list_entity_properties as list_entity_properties_cmd,
)

logger = get_logger(__name__)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer", "maintainer"]))]
)


@router.get("/v2/canonical/entities", tags=["ontology"],
            include_in_schema=sys_config.expose_gui_api)
async def list_canonical_entities(query: str = None, limit: int = 100, start: int = 0, output: str = 'entity'):
    records, count = await list_canonical_entities_cmd(query, limit, start, output)
    return {
        "total": count,
        "grouped": {
            "Canonical Entities": records
        }
    }


@router.get("/v2/canonical/entity/{entity_id}/properties", tags=["ontology"],
            include_in_schema=sys_config.expose_gui_api)
async def list_entity_properties(entity_id: str, output: str = 'entity'):
    return await list_entity_properties_cmd(entity_id, output)
