import urllib.parse
from typing import List, Union, Optional
from json import JSONDecodeError

from fastapi import APIRouter, Request, status, HTTPException, Header, Depends
from fastapi.responses import RedirectResponse

from airembr.system.command.collect.errors import CollectorError
from airembr.system.command.collect.observations import collect_observations
from airembr.system.command.collect.observation_entities import \
    add_entities_to_observation as add_entities_to_observation_cmd
from airembr.system.command.collect.webhook_observation import collect_webhook_observation
from airembr.system.command.collect.redirect_observation import collect_redirect_observation
from airembr.system.command.collect.simplified_observation import collect_simplified_observation
from airembr.model.system.headers import Headers
from airembr.model.api.request.observation import Observation, ObservationEntity
from airembr.system.process.logging.log_handler import get_logger
from airembr.system.adapter.metadata.mysql.service.bridge_service import BridgeService
from airembr.model.payload.simplified_observation import SimplifiedObservation
from airembr.system.config.sys_config import sys_config

from airembr_api.endpoint.collector.auth.jwt_auth import JWTAuth

from pararun.protocol.queue_client_protocol import QUEUE_BACK_PRESSURE, MESSAGE_TOO_LARGE, INTERNAL_ERROR

logger = get_logger(__name__)

router = APIRouter()
bs = BridgeService()
jwt_auth = JWTAuth()
tasks = []


def _parse_url_query_params_to_dict(url_query_params):
    params = dict(urllib.parse.parse_qs(url_query_params))
    for key, value in params.items():
        if len(value) == 1:
            params[key] = value[0]
    return params


async def _parse_body(request: Request):
    if request.headers.get('Content-Type', '').lower().startswith('application/json'):
        try:
            return await request.json()
        except JSONDecodeError:
            raise ValueError(f"Could not parse body content to JSON. Body content {await request.body()}")
    elif request.headers.get('Content-Type', '').lower() in ['multipart/form-data',
                                                             'application/x-www-form-urlencoded']:
        return await request.form()
    else:
        return await request.body()


def _raise_for_dispatch_status(dispatch_status):
    # No dispatch_status if not sent to the queue
    if dispatch_status:
        if dispatch_status.status == QUEUE_BACK_PRESSURE:
            raise HTTPException(detail=str(dispatch_status.error), status_code=dispatch_status.status)
        if dispatch_status.status == MESSAGE_TOO_LARGE:
            raise HTTPException(detail=str(dispatch_status.error), status_code=dispatch_status.status)
        if dispatch_status.status == INTERNAL_ERROR:
            raise HTTPException(detail=str(dispatch_status.error), status_code=dispatch_status.status)


@router.post("/", tags=['collector'], status_code=status.HTTP_202_ACCEPTED, responses={
    200: {"description": "Processed immediately"},
    202: {"description": "Accepted for async processing"},
    500: {"description": "Error"},
}, )
@router.put("/", tags=['collector'], status_code=status.HTTP_202_ACCEPTED, responses={
    200: {"description": "Processed immediately"},
    202: {"description": "Accepted for async processing"},
    500: {"description": "Error"},
}, )
async def collect_facts(observations: Union[List[Observation], Observation],
                        request: Request,
                        claims: dict = Depends(jwt_auth)):
    try:
        conversation_memory, dispatch_status = await collect_observations(observations, Headers(request.headers))
        # No dispatch_status if not sent to the queue
        if dispatch_status:
            if dispatch_status.status == QUEUE_BACK_PRESSURE:
                raise HTTPException(detail=str(dispatch_status.error), status_code=dispatch_status.status)
            if dispatch_status.status == MESSAGE_TOO_LARGE:
                raise HTTPException(detail=str(dispatch_status.error), status_code=dispatch_status.status)
            if dispatch_status.status == INTERNAL_ERROR:
                raise HTTPException(detail=str(dispatch_status.error), status_code=dispatch_status.status)

        return conversation_memory

    except CollectorError as e:
        raise HTTPException(detail=str(e), status_code=e.status_code)


@router.patch("/observation/{observation_id}/entities/observer/{observer_type}/{observer_id}",
              tags=['collector'], status_code=status.HTTP_202_ACCEPTED,
              responses={
                  200: {"description": "Processed immediately"},
                  202: {"description": "Accepted for async processing"},
                  500: {"description": "Error"},
              }, )
async def add_entities_to_observation(
        observation_id: str,
        observer_type: str,
        observer_id: str,
        entities: List[ObservationEntity],
        request: Request,
        claims: dict = Depends(jwt_auth)):
    try:
        _, dispatch_status = await add_entities_to_observation_cmd(
            observation_id, observer_type, observer_id, entities, Headers(request.headers))
        _raise_for_dispatch_status(dispatch_status)
    except CollectorError as e:
        raise HTTPException(detail=str(e), status_code=e.status_code)


@router.get("/", tags=['collector'])
async def info():
    return {
        "name": sys_config.app_name,
        "version": sys_config.version.version,
    }


@router.put("/webhook/{source_id}", tags=['collector'])
@router.post("/webhook/{source_id}", tags=['collector'])
async def track_webhook_post_put(source_id: str, request: Request):
    """
    Collects data as webhook call.
    """
    try:
        body = await _parse_body(request)
        _, dispatch_status = await collect_webhook_observation(
            source_id.strip(), dict(request.query_params), body, Headers(request.headers))
        _raise_for_dispatch_status(dispatch_status)
    except CollectorError as e:
        raise HTTPException(detail=str(e), status_code=e.status_code)


@router.get("/webhook/{source_id}", tags=['collector'])
async def track_webhook_get(source_id: str, request: Request):
    """
    Collects data from request POST and adds event type. It stays profile-less.
    """
    try:
        body = _parse_url_query_params_to_dict(request.url.query)
        _, dispatch_status = await collect_webhook_observation(
            source_id.strip(), dict(request.query_params), body, Headers(request.headers))
        _raise_for_dispatch_status(dispatch_status)
    except CollectorError as e:
        raise HTTPException(detail=str(e), status_code=e.status_code)


@router.get("/redirect/{source_id}", tags=["redirect"])
async def request_redirect(request: Request, source_id: str):
    """
       Redirects events
    """
    params = _parse_url_query_params_to_dict(request.url.query)
    headers = Headers(request.headers)

    try:
        redirect_url = await collect_redirect_observation(source_id.strip(), params, headers)
    except CollectorError as e:
        raise HTTPException(detail=str(e), status_code=e.status_code)

    return RedirectResponse(redirect_url)


@router.post("/observe/{name}/{id}", tags=['collector'])
async def simplified_observation(request: Request,
                                 name: str,
                                 payload: SimplifiedObservation,
                                 x_source: Optional[str] = Header(None),
                                 id: Optional[str] = None,
                                 claims: dict = Depends(jwt_auth)):
    if x_source is None:
        raise HTTPException(detail="Assess denied. Incorrect or unset source Id token.", status_code=403)

    try:
        conversation_memory, dispatch_status = await collect_simplified_observation(
            name, id, x_source, payload, Headers(request.headers))
        _raise_for_dispatch_status(dispatch_status)
    except CollectorError as e:
        raise HTTPException(detail=str(e), status_code=e.status_code)

    return conversation_memory
