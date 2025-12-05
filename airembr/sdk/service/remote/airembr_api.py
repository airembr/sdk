import random
from typing import Optional, Protocol, Dict, Any, Tuple

import requests

from airembr.sdk.model.memory.conversation_memory import ConversationMemory, MemorySessions
from airembr.sdk.model.query.response import QueryResponse, QueryEntityResponse

from airembr.sdk.model.query.status import QueryStatus
from airembr.sdk.model.query.time_range_query import DatetimeRangePayload, DatePayload


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
        self.context = context if context else "staging"
        self.tenant = tenant

    def get_default_headers(self):
        headers = {
            "Content-Type": "application/json",
            "x-context": self.context,

        }
        if self.tenant:
            headers["x-tenant"] = self.tenant

        return headers

    def _get_headers(self, realtime: Optional[str] = None, skip: Optional[str] = None, response: bool = True,
                     context: Optional[str] = None, tenant: Optional[str] = None):
        headers = {
            "user-agent": "AiRembrSdkClient/0.0.1",
            "accept": "application/json"
        }

        if tenant:
            headers["x-tenant"] = tenant
        else:
            headers["x-tenant"] = self.tenant

        if skip:
            headers["x-skip"] = skip

        if realtime:
            headers["x-realtime"] = realtime

        if response:
            headers["x-conversation-response"] = "1"

        if context:
            headers["x-context"] = context
        else:
            headers["x-context"] = context if context else "staging"

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

    def remember(self, data, realtime: Optional[str] = None, skip: Optional[str] = None, response: bool = True,
                 context: Optional[str] = None, tenant: Optional[str] = None) -> Tuple[QueryStatus, MemorySessions]:

        response = requests.post(self.url, headers=self._get_headers(realtime, skip, response, context, tenant),
                                 json=data)

        body = response.json()

        return QueryStatus(response.status_code), MemorySessions(
            {key: ConversationMemory(**value) for key, value in body.items()} if response else {})

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
                    min_date: Optional[DatePayload] = None,
                    max_date: Optional[DatePayload] = None,
                    page: Optional[int] = 0,
                    limit: Optional[int] = 30,
                    timezone: Optional[str] = "UTC",
                    headers=None,
                    ) -> Tuple[
        QueryStatus, QueryResponse]:

        url = f"{self.url}/v2/events/list/page/{page}"

        data = DatetimeRangePayload(
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
