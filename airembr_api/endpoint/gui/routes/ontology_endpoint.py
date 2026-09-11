from typing import Optional

from fastapi import APIRouter, Depends, Response

from airembr.system.process.logging.log_handler import get_logger
from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr.model.metadata.sys_ontology import Ontology
from airembr.system.config.sys_config import sys_config
from airembr.system.command.ontology.ontology import (
    list_ontologies as list_ontologies_cmd,
    get_ontology as get_ontology_cmd,
    save_ontology as save_ontology_cmd,
    delete_ontology as delete_ontology_cmd,
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


@router.get("/v2/ontology/{id}", tags=["ontology"],
            response_model=Optional[Ontology],
            include_in_schema=sys_config.expose_gui_api)
async def load_ontology_by_id(id: str, response: Response):
    record = await get_ontology_cmd(id)
    if not record:
        response.status_code = 404
        return None
    return record


@router.post("/v2/ontology", tags=["ontology"],
             include_in_schema=sys_config.expose_gui_api)
async def save_ontology(ontology: Ontology):
    return await save_ontology_cmd(ontology)


@router.delete("/v2/ontology/{id}", tags=["ontology"],
               include_in_schema=sys_config.expose_gui_api)
async def delete_ontology(id: str):
    return await delete_ontology_cmd(id)
