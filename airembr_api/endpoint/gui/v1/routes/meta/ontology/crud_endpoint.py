from typing import Optional

from fastapi import APIRouter, Depends, Response

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions
from airembr.model.metadata.sys_ontology import Ontology
from airembr.system.config.sys_config import sys_config
from airembr.system.command.v1.meta.ontology.ontology import (
    get_ontology as get_ontology_cmd,
    save_ontology as save_ontology_cmd,
    delete_ontology as delete_ontology_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer", "maintainer"]))]
)


@router.get("/v1/ontology/{id}", tags=["ontology"],
            response_model=Optional[Ontology],
            include_in_schema=sys_config.expose_gui_api)
@router.get("/v2/ontology/{id}", tags=["ontology"],
            response_model=Optional[Ontology],
            include_in_schema=sys_config.expose_gui_api)
async def get_ontology_by_id(id: str, response: Response):
    record = await get_ontology_cmd(id)
    if not record:
        response.status_code = 404
        return None
    return record


@router.post("/v1/ontology", tags=["ontology"],
             include_in_schema=sys_config.expose_gui_api)
@router.post("/v2/ontology", tags=["ontology"],
             include_in_schema=sys_config.expose_gui_api)
async def save_ontology(ontology: Ontology):
    return await save_ontology_cmd(ontology)


@router.delete("/v1/ontology/{id}", tags=["ontology"],
               include_in_schema=sys_config.expose_gui_api)
@router.delete("/v2/ontology/{id}", tags=["ontology"],
               include_in_schema=sys_config.expose_gui_api)
async def delete_ontology_by_id(id: str):
    return await delete_ontology_cmd(id)
