from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi.responses import Response

from airembr.system.command.entity.errors import EntityError
from airembr.system.command.entity.entity import (
    get_profile_logs as get_profile_logs_cmd,
    count_profiles as count_profiles_cmd,
    get_entity_by_hash as get_entity_by_hash_cmd,
    get_temporal_entity_by_entity_pk as get_temporal_entity_by_entity_pk_cmd,
    get_entity_columns as get_entity_columns_cmd,
    list_entities_by_type_page as list_entities_by_type_page_cmd,
    get_observation_entities_for_observer as get_observation_entities_for_observer_cmd,
    get_entities_from_observation as get_entities_from_observation_cmd,
    list_entity_snapshots as list_entity_snapshots_cmd,
)

from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer", "maintainer"]))]
)


@router.get("/entity/{entity_name}/logs/{entity_id}", tags=["log"],
            dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer"]))],
            include_in_schema=sys_config.expose_gui_api)
async def get_profile_logs(entity_name: str, entity_id: str, sort: str = None):
    """
    Gets logs for profile with given ID (str)
    """

    records, total = await get_profile_logs_cmd(entity_name, entity_id, sort)
    return {
        "result": records,
        "total": total
    }


@router.get("/entity/{entity_name}/count", tags=["entity"],
            include_in_schema=sys_config.expose_gui_api)
async def count_profiles(entity_name: str):
    return await count_profiles_cmd(entity_name)


@router.get("/entity/{entity_type}/hash/{hash}", tags=["entity"],
            dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer"]))],
            include_in_schema=sys_config.expose_gui_api)
async def get_entity_by_hash(entity_type: str, hash: str, response: Response) -> Optional[dict]:
    """
    Returns entity by its id
    """

    result = await get_entity_by_hash_cmd(entity_type, hash)

    if result is None:
        response.status_code = 404
        return None

    return result


# Not used
# @router.get("/v2/entity/{entity_id}", tags=["entity"],
#             dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer"]))],
#             include_in_schema=sys_config.expose_gui_api)
# async def get_event_entities_by_entity_id(entity_id: str, response: Response):
#     result = await bd_entity_adapter.load_entity_by_id(entity_id)
#     if result is None:
#         response.status_code = 404
#         return None
#
#     return result


@router.get("/v2/entity/pk/{entity_pk}/data_hash/{data_hash}", tags=["entity"],
            dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer"]))],
            include_in_schema=sys_config.expose_gui_api)
async def get_temporal_entity_by_entity_pk(entity_pk: str, data_hash: str, response: Response):
    """
    Temporal entities are entities with traits that were delivered during fact collection.
    They do not contain the current state, only the state at the time of fact collection.
    """
    result = await get_temporal_entity_by_entity_pk_cmd(entity_pk, data_hash)
    if result is None:
        response.status_code = 404
        return None

    return result


@router.get('/v2/entity/{table_name}/columns', tags=['entity'], include_in_schema=sys_config.expose_gui_api)
async def get_entity_columns(table_name: str):
    return await get_entity_columns_cmd(table_name)


@router.get('/v2/entities/{entity_type}/page/{page}', tags=['entity'], include_in_schema=sys_config.expose_gui_api)
async def list_entities_by_type_page(entity_type: str, page: int):
    return await list_entities_by_type_page_cmd(entity_type, page)


@router.get('/v2/entities/observation/{observation_id}/observer/{observer_pk}', tags=['entity'],
            include_in_schema=sys_config.expose_gui_api)
async def get_observation_entities_for_observer(observation_id: str, observer_pk: str):
    return await get_observation_entities_for_observer_cmd(observation_id, observer_pk)


@router.get('/v2/entities/observation/{observation_id}', tags=['entity'],
            include_in_schema=sys_config.expose_gui_api)
async def get_entities_from_observation(observation_id: str):
    """
    Gets entities for given observation regardless observer
    """

    return await get_entities_from_observation_cmd(observation_id)


@router.get("/v2/entity/1/list", tags=["v2/data"], include_in_schema=sys_config.expose_gui_api)
async def list_of_entity_snapshots(query: str, entity_type: Optional[str] = None, observer: Optional[str] = None,
                                   page: Optional[int] = 0):
    try:
        return await list_entity_snapshots_cmd(query, entity_type, observer, page)
    except EntityError as e:
        raise HTTPException(detail=str(e), status_code=e.status_code)
