from fastapi import APIRouter, Depends

from airembr.system.process.logging.log_handler import get_logger
from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config
from airembr.system.command.ontology.ontology import (
    list_ontologies as list_ontologies_cmd,
)

logger = get_logger(__name__)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer", "maintainer"]))]
)


@router.get("/v2/ontologies", tags=["ontology"],
            include_in_schema=sys_config.expose_gui_api)
async def list_ontologies(query: str = None, limit: int = 100, start: int = 0, output: str = 'entity'):
    records, count = await list_ontologies_cmd(query, limit, start, output)
    return {"total": count, "grouped": {"Ontologies": records}}
