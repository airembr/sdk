from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from airembr.model.system.answer import Answer
from airembr.system.command.eql.errors import EqlError
from airembr.system.command.eql.recall_with_text import recall_with_text as recall_with_text_cmd
from airembr.system.command.eql.search_facts import get_observation_facts as get_observation_facts_cmd
from airembr.system.command.eql.search_locations import get_located_observation_entities as \
    get_located_observation_entities_cmd
from airembr.system.command.eql.search_observations import get_observations as get_observations_cmd
from airembr.system.command.eql.search_entity_types import get_observation_entity_types as \
    get_observation_entity_types_cmd
from airembr.system.command.eql.autocomplete import autocomplete_eql as autocomplete_eql_cmd
from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer"]))]
)


@router.get("/v2/eql/text", response_model=Answer, include_in_schema=sys_config.expose_gui_api)
async def recall_with_text(query: str, start: int = 0,
                           limit: int = 1000,
                           unmatched_entities: int = 0,
                           unmatched_traits: int = 0,
                           min_score: float = 0.65,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None):
    """
    Example:
    ```
        Any semantic query: When did I pay for my VW Passat insurance.
    ```
    """
    try:
        return await recall_with_text_cmd(query, start, limit, unmatched_entities, unmatched_traits, min_score,
                                          start_date, end_date)
    except EqlError as e:
        raise HTTPException(detail=str(e), status_code=e.status_code)


@router.get("/v2/eql/facts", include_in_schema=sys_config.expose_gui_api)
async def get_observation_facts(query: str,
                                observer_pk: Optional[str] = None,
                                unmatched_entities: int = 0,
                                unmatched_traits: int = 0,
                                start: int = 0,
                                limit: int = 500,
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None):
    try:
        return await get_observation_facts_cmd(query, unmatched_entities, unmatched_traits, start, limit, start_date,
                                               end_date)
    except EqlError as e:
        raise HTTPException(detail=str(e), status_code=e.status_code)


@router.get("/v2/eql/entity/locations", include_in_schema=sys_config.expose_gui_api)
async def get_located_observation_entities(query: str,
                                           unmatched_entities: Optional[int] = 0,
                                           unmatched_traits: Optional[int] = 0,
                                           entity_types: List[str] = Query(default=None),
                                           start_date: Optional[datetime] = None,
                                           end_date: Optional[datetime] = None,
                                           traits_source: str = "property_state"):
    try:
        return await get_located_observation_entities_cmd(query, entity_types, unmatched_entities, unmatched_traits,
                                                           start_date, end_date, traits_source=traits_source)
    except EqlError as e:
        raise HTTPException(detail=str(e), status_code=e.status_code)


@router.get("/v2/eql/observations", include_in_schema=sys_config.expose_gui_api)
async def get_observations(query: str,
                           unmatched_entities: Optional[int] = 0,
                           unmatched_traits: Optional[int] = 0,
                           start: Optional[int] = 0,
                           limit: Optional[int] = 500,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None):
    try:
        return await get_observations_cmd(query, unmatched_entities, unmatched_traits, start, limit, start_date,
                                          end_date)
    except EqlError as e:
        raise HTTPException(detail=str(e), status_code=e.status_code)


@router.get("/v2/eql/entity-types", include_in_schema=sys_config.expose_gui_api)
async def get_observation_entity_types(query: str,
                                       unmatched_entities: Optional[int] = 0,
                                       unmatched_traits: Optional[int] = 0,
                                       start_date: Optional[datetime] = None,
                                       end_date: Optional[datetime] = None,
                                       with_locations: bool = False):
    try:
        return await get_observation_entity_types_cmd(query, unmatched_entities, unmatched_traits, start_date,
                                                       end_date, with_locations)
    except EqlError as e:
        raise HTTPException(detail=str(e), status_code=e.status_code)


@router.get("/v2/eql/autocomplete", tags=["eql"], include_in_schema=sys_config.expose_gui_api)
async def autocomplete_eql(query: str):
    try:
        return await autocomplete_eql_cmd(query)
    except EqlError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
