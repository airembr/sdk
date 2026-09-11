from typing import Optional

from fastapi import APIRouter, Depends, Response

from airembr.system.process.logging.log_handler import get_logger
from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr.model.metadata.sys_canonical_entity import CanonicalEntity, CanonicalEntityProperty
from airembr.system.config.sys_config import sys_config
from airembr.system.command.canonical.entities import (
    list_canonical_entities as list_canonical_entities_cmd,
    get_canonical_entity as get_canonical_entity_cmd,
    save_canonical_entity as save_canonical_entity_cmd,
    delete_canonical_entity as delete_canonical_entity_cmd,
)
from airembr.system.command.canonical.properties import (
    list_entity_properties as list_entity_properties_cmd,
    get_entity_property as get_entity_property_cmd,
    save_entity_property as save_entity_property_cmd,
    delete_entity_property as delete_entity_property_cmd,
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


@router.get("/v2/canonical/entity/{id}", tags=["ontology"],
            response_model=Optional[CanonicalEntity],
            include_in_schema=sys_config.expose_gui_api)
async def load_canonical_entity_by_id(id: str, response: Response):
    record = await get_canonical_entity_cmd(id)
    if not record:
        response.status_code = 404
        return None
    return record


@router.post("/v2/canonical/entity", tags=["ontology"],
             include_in_schema=sys_config.expose_gui_api)
async def save_canonical_entity(entity: CanonicalEntity):
    return await save_canonical_entity_cmd(entity)


@router.delete("/v2/canonical/entity/{id}", tags=["ontology"],
               include_in_schema=sys_config.expose_gui_api)
async def delete_canonical_entity(id: str):
    return await delete_canonical_entity_cmd(id)


# --- property endpoints ---

@router.get("/v2/canonical/entity/{entity_id}/properties", tags=["ontology"],
            include_in_schema=sys_config.expose_gui_api)
async def list_entity_properties(entity_id: str, output: str = 'entity'):
    return await list_entity_properties_cmd(entity_id, output)


@router.get("/v2/canonical/entity/property/{id}", tags=["ontology"],
            response_model=Optional[CanonicalEntityProperty],
            include_in_schema=sys_config.expose_gui_api)
async def load_entity_property(id: str, response: Response):
    prop = await get_entity_property_cmd(id)
    if not prop:
        response.status_code = 404
        return None
    return prop


@router.post("/v2/canonical/entity/{entity_id}/property", tags=["ontology"],
             include_in_schema=sys_config.expose_gui_api)
async def save_entity_property(entity_id: str, prop: CanonicalEntityProperty):
    return await save_entity_property_cmd(entity_id, prop)


@router.delete("/v2/canonical/entity/property/{id}", tags=["ontology"],
               include_in_schema=sys_config.expose_gui_api)
async def delete_entity_property(id: str):
    return await delete_entity_property_cmd(id)
