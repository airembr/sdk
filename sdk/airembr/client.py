from typing import List, Optional, Tuple

from sdk.airembr.model.memory.conversation_memory import MemorySessions
from sdk.airembr.model.observation import Observation
from sdk.airembr.model.query.response import QueryEntityResponse
from sdk.airembr.model.query.status import QueryStatus
from sdk.airembr.model.query.time_range_query import DatePayload
from sdk.airembr.service.api.sync_api import SyncApi


class AirembrQuery:
    def __init__(self, transport):
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
              timezone: Optional[str] = "UTC",
              headers=None, ):

        if query is None:
            query = ""

        status, result = self.transport.query_facts(query, min_date, max_date, page, limit, timezone, headers=headers)

        if not status.ok():
            raise ConnectionError(f"Query failed with status: {status} and result: {result}")

        return result


class AirembrClient:

    def __init__(self, api):
        self.transport = SyncApi(api)

    def observe(self,
                observations: List[Observation],
                realtime: Optional[str] = None,
                skip: Optional[str] = None,
                response: bool = True,
                context: Optional[str] = None) -> Tuple[QueryStatus, MemorySessions]:
        payload = [observation.model_dump(mode="json") for observation in observations]

        return self.transport.remember(payload, realtime, skip, response, context=context)

    def authenticate(self, username: str, password: str) -> "AirembrClient":
        status, _ = self.transport.authenticate(username, password)
        if not status.ok():
            raise ConnectionError("Authentication failed.")
        return self

    @property
    def query(self) -> AirembrQuery:
        return AirembrQuery(self.transport)
