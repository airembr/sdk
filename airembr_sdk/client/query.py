from typing import List, Optional, Tuple

from airembr.model.system.query.time_range_query import DatePayload

from airembr_sdk.api.model.collection.response import QueryEntityResponse, QueryResponse
from airembr_sdk.api.model.collection.response_status import QueryStatus
from airembr_sdk.api.model.collection.conversation_memory import MemorySessions
from airembr_sdk.api.model.collection.observation import IObservation
from airembr_sdk.client.airembr_api import AirembrApi


class AirembrQuery:
    def __init__(self, transport: AirembrApi):
        self.transport = transport

    def stitched_entity(self, query, entity_type: str) -> QueryEntityResponse:
        status, result = self.transport.query_stitched_entity(query, entity_type)
        if not status.ok():
            raise ConnectionError(f"Query failed with status: {status} and result: {result}")
        return result

    def computed_entity(self, query, entity_type: str = None) -> QueryEntityResponse:
        status, result = self.transport.query_computed_entity(query, entity_type)
        if not status.ok():
            raise ConnectionError(f"Query failed with status: {status} and result: {result}")
        return result

    def facts(self,
              query: Optional[str] = None,
              min_date: Optional[DatePayload] = None,
              max_date: Optional[DatePayload] = None,
              page: Optional[int] = 0,
              limit: Optional[int] = 30,
              timezone: Optional[str] = "UTC") -> QueryResponse:

        if query is None:
            query = ""

        status, result = self.transport.query_facts(query, min_date, max_date, page, limit, timezone,
                                                    headers=self.transport.get_default_headers())

        if not status.ok():
            raise ConnectionError(f"Query failed with status: {status} and result: {result}")

        return result


class AirembrClient:

    def __init__(self, api):
        self.transport = AirembrApi(api)

    def observe(self,
                observations: List[IObservation],
                realtime: Optional[str] = None,
                skip: Optional[str] = None,
                bridge: Optional[str] = None,
                response: bool = True,
                context: Optional[str] = None) -> Tuple[QueryStatus, MemorySessions]:
        payload = [observation.model_dump(mode="json") for observation in observations]

        return self.transport.remember(payload,
                                       realtime,
                                       skip,
                                       response,
                                       bridge,
                                       context=context)

    def authenticate(self, username: str, password: str) -> "AirembrClient":
        status, _ = self.transport.authenticate(username, password)
        if not status.ok():
            raise ConnectionError("Authentication failed.")
        return self

    @property
    def query(self) -> AirembrQuery:
        return AirembrQuery(self.transport)


class AirembrChatPeer:

    def peer(self, type: str):
        pass