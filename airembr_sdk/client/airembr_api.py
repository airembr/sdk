import random
from datetime import datetime
from typing import Optional, Protocol, Dict, Any, Tuple, List, Union

import requests

from airembr.model.system.header_schema import X_REAL_TIME, X_SKIP, X_TENANT, X_CONTEXT, X_BRIDGE, \
    X_CONVERSATION_RESPONSE, V_STAGING
from airembr_sdk.model.interface.i_time_range import IDatetimeRangePayload, IDatePayload
from airembr_sdk.model.interface.i_response import QueryResponse, QueryEntityResponse
from airembr_sdk.model.core.value.response_status import QueryStatus
from airembr_sdk.model.interface.i_conversation_memory import IConversationMemory, IMemorySessions
from airembr_sdk.model.interface.i_observation import IObservationEntity
from airembr_sdk.logging.log_handler import get_logger

logger = get_logger(__name__)


class ApiProtocol(Protocol):
    url: str
    headers: Dict[str, str]
    response: bool
    skip: Optional[str]
    realtime: Optional[str]

    def __init__(
            self,
            url: str
    ) -> None: ...

    def remember(self, data: Dict[str, Any], realtime: Optional[str] = None, skip: Optional[str] = None,
                 response: bool = True,
                 context: Optional[str] = None) -> Tuple[int, Dict[str, Any]]: ...

    def query_computed_entity(self, query, entity_type: str = None, page: int = 0, headers=None) -> Tuple[
        int, Dict[str, Any]]: ...

    def query_stitched_entity(self, query, entity_type: str = None, page: int = 0, headers=None) -> Tuple[
        QueryStatus, QueryResponse]: ...


class AirembrApi:

    def __init__(self, url: str, context: Optional[str] = None, tenant: Optional[str] = None):
        self.url = url
        self.token = None
        self.token_type = None
        self.context = context if context else V_STAGING
        self.tenant = tenant

    def get_default_headers(self):
        headers = {
            "Content-Type": "application/json",
            X_CONTEXT: self.context,

        }
        if self.tenant:
            headers[X_TENANT] = self.tenant

        return headers

    def _get_headers(self,
                     realtime: Optional[str] = None,
                     skip: Optional[str] = None,
                     response: bool = True,
                     context: Optional[str] = None,
                     tenant: Optional[str] = None,
                     bridge: Optional[str] = None,
                     ):
        headers = {
            "user-agent": "AiRembrSdkClient/0.0.1",
            "accept": "application/json"
        }

        if tenant:
            headers[X_TENANT] = tenant
        else:
            headers[X_TENANT] = self.tenant

        if skip:
            headers[X_SKIP] = skip

        if realtime:
            headers[X_REAL_TIME] = realtime

        if response:
            headers[X_CONVERSATION_RESPONSE] = "1"

        if context:
            headers[X_CONTEXT] = context
        else:
            headers[X_CONTEXT] = context if context else V_STAGING

        if bridge:
            headers[X_BRIDGE] = bridge

        if self.token:
            headers['Authorization'] = self._get_token()

        return headers

    def _get_token(self):
        return f"{self.token_type} {self.token}"

    def authenticate(self, username: str, password: str) -> Tuple[QueryStatus, Dict[str, Any]]:

        url = f"{self.url}/user/token"

        headers = {
            "user-agent": "AiRembrSdkClient/0.0.1",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "password",
            "username": username,
            "password": password
        }

        response = requests.post(url, headers=headers, data=data)
        payload = response.json()
        self.token = payload["access_token"]
        self.token_type = payload["token_type"]

        return QueryStatus(response.status_code), payload

    def authenticate_with_secret(self, secret: str) -> Tuple[QueryStatus, Dict[str, Any]]:

        url = f"{self.url}/auth"

        response = requests.post(url, headers={"Content-Type": "application/json"}, json={"secret": secret})
        payload = response.json()

        if response.ok:
            self.token = payload["access_token"]
            self.token_type = payload.get("token_type", "bearer")

        return QueryStatus(response.status_code), payload

    def remember(self,
                 data,
                 realtime: Optional[str] = None,
                 skip: Optional[str] = None,
                 response: bool = True,
                 bridge: Optional[str] = None,
                 context: Optional[str] = None,
                 tenant: Optional[str] = None) -> Tuple[QueryStatus, IMemorySessions]:

        logger.debug(f"Request sent to POST: {self.url}")
        _response = requests.post(self.url,
                                 headers=self._get_headers(
                                     realtime,
                                     skip,
                                     response,
                                     context,
                                     tenant,
                                     bridge
                                 ),
                                 json=data)

        body = _response.json()

        return QueryStatus(_response.status_code), IMemorySessions(
            {key: IConversationMemory(**value) for key, value in body.items()} if _response else {})

    def add_entities_to_observation(self,
                                    observation_id: str,
                                    observer_type: str,
                                    observer_id: str,
                                    entities: List[Union[Dict[str, Any], IObservationEntity]],
                                    realtime: Optional[str] = None) -> Tuple[
        QueryStatus, Any]:

        url = f"{self.url}/observation/{observation_id}/entities/observer/{observer_type}/{observer_id}"

        payload = [
            entity if isinstance(entity, dict) else entity.model_dump(mode="json", exclude_none=True)
            for entity in entities
        ]

        response = requests.patch(url, headers=self._get_headers(realtime=realtime), json=payload)

        try:
            body = response.json()
        except ValueError:
            body = {"detail": response.text}

        return QueryStatus(response.status_code), body

    def ask(self,
            query: str,
            start: int = 0,
            limit: int = 1000,
            unmatched_entities: int = 0,
            unmatched_traits: int = 0,
            min_score: float = 0.65,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None) -> Tuple[QueryStatus, Dict[str, Any]]:

        if not self.token:
            raise Exception("Not authenticated")

        url = f"{self.url}/v2/eql/text"
        params = {
            "query": query,
            "start": start,
            "limit": limit,
            "unmatched_entities": unmatched_entities,
            "unmatched_traits": unmatched_traits,
            "min_score": min_score,
        }
        if start_date is not None:
            params["start_date"] = start_date.isoformat()
        if end_date is not None:
            params["end_date"] = end_date.isoformat()

        headers = self._get_headers()
        headers['Authorization'] = self._get_token()

        response = requests.get(url, headers=headers, params=params)

        try:
            body = response.json()
        except ValueError:
            body = {"detail": response.text}

        return QueryStatus(response.status_code), body

    def search_observations(self,
                            query: str,
                            unmatched_entities: int = 0,
                            unmatched_traits: int = 0,
                            start: int = 0,
                            limit: int = 500,
                            start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None) -> Tuple[QueryStatus, List[Dict[str, Any]]]:

        if not self.token:
            raise Exception("Not authenticated")

        url = f"{self.url}/v2/eql/observations"
        params = {
            "query": query,
            "unmatched_entities": unmatched_entities,
            "unmatched_traits": unmatched_traits,
            "start": start,
            "limit": limit,
        }
        if start_date is not None:
            params["start_date"] = start_date.isoformat()
        if end_date is not None:
            params["end_date"] = end_date.isoformat()

        headers = self._get_headers()
        headers['Authorization'] = self._get_token()

        response = requests.get(url, headers=headers, params=params)

        try:
            body = response.json()
        except ValueError:
            body = {"detail": response.text}

        return QueryStatus(response.status_code), body

    def query_computed_entity(self, query, entity_type: str = None, page: int = 0, headers=None) -> Tuple[
        QueryStatus, QueryEntityResponse]:
        url = f"{self.url}/v2/entity/1/list"
        params = {
            "page": page,
            "query": query
        }

        if not self.token:
            raise Exception("Not authenticated")

        if headers is None:
            headers = {}

        headers['Authorization'] = self._get_token()

        if entity_type:
            params["entity_type"] = entity_type

        response = requests.get(url, headers=headers, params=params)

        result = response.json()

        return QueryStatus(response.status_code), QueryEntityResponse(result=result.get('result', []),
                                                                      total=result.get('total', 0))

    def query_stitched_entity(self, query, entity_type: str, page: int = 0, headers=None) -> Tuple[
        QueryStatus, QueryEntityResponse]:
        url = f"{self.url}/v2/entity/2/list"
        params = {
            "page": page,
            "query": query
        }

        if not self.token:
            raise Exception("Not authenticated")

        if headers is None:
            headers = {}

        headers['Authorization'] = self._get_token()

        if entity_type:
            params["entity_type"] = entity_type

        response = requests.get(url, headers=headers, params=params)

        result = response.json()

        return QueryStatus(response.status_code), QueryEntityResponse(result=result.get('result', []),
                                                                      total=result.get('total', 0))

    def query_facts(self,
                    query: str,
                    min_date: Optional[IDatePayload] = None,
                    max_date: Optional[IDatePayload] = None,
                    page: Optional[int] = 0,
                    limit: Optional[int] = 30,
                    timezone: Optional[str] = "UTC",
                    headers=None,
                    ) -> Tuple[
        QueryStatus, QueryResponse]:

        url = f"{self.url}/v2/events/list/page/{page}?shorten=false"

        data = IDatetimeRangePayload(
            start=page,
            limit=limit,
            minDate=min_date,
            maxDate=max_date,
            timeZone=timezone,
            rand=random.random(),
            where=query
        )

        if not self.token:
            raise Exception("Not authenticated")

        if headers is None:
            headers = {}

        headers['Authorization'] = self._get_token()

        response = requests.post(url, headers=headers, json=data.model_dump(mode='json'))

        result = response.json()

        return QueryStatus(response.status_code), QueryResponse(result=result.get('result', []),
                                                                total=result.get('total', 0))
