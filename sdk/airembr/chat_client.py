from datetime import datetime
from typing import Optional, Tuple, List, Union
from uuid import uuid4

from sdk.airembr.model.instance_link import InstanceLink
from sdk.airembr.model.memory.conversation_memory import MemorySessions
from sdk.airembr.model.observation import Observation
from sdk.airembr.model.query.status import QueryStatus
from sdk.airembr.service.api.sync_api import SyncApi
from sdk.airembr.service.time.time import now_in_utc


class AiRembrChatClient:

    def __init__(self,
                 api: str,
                 source_id: str,
                 entities,
                 observer: InstanceLink,
                 chat_id: str, chat_ttl: int = 60 * 60,
                 tenant_id: Optional[str] = None,
                 observation_id: Optional[str] = None
                 ):
        self.observation_id = observation_id
        self.observer = observer
        self.entities = entities

        self.api = api
        self.chat_ttl = chat_ttl
        self.source_id = source_id
        self.chat_id = chat_id
        self.chats = []

    def chat(self, message: str, actor: InstanceLink, objects: List[InstanceLink]=None, date: Optional[Union[datetime|str]] = None,
             fact_label: Optional[str] = 'messaged', observer: Optional[InstanceLink]=None):

        if date is not None and isinstance(date, str):
            date = datetime.fromisoformat(date)

        chat = {
            "ts": now_in_utc() if date is None else date,
            "type": "chat",
            "label": fact_label,
            "observer": self.observer if observer is None else observer,
            "actor": actor,
            "objects": objects,
            "semantic": {
                "summary": message
            }
        }

        self.chats.append(chat)

    def remember(self,
                 realtime: Optional[str] = None,
                 skip: Optional[str] = None,
                 response: bool = True,
                 context: Optional[str] = None) -> Tuple[QueryStatus, MemorySessions]:
        if not self.chats:
            return QueryStatus(404), MemorySessions({})

        payload = self.get_observation()

        transport = SyncApi(self.api)
        payload = payload.model_dump(mode="json")

        return transport.remember(
            [payload],
            realtime, skip, response, context
        )

    def get_observation(self) -> Observation:
        return Observation(**{
            "id": str(uuid4()) if self.observation_id is None else self.observation_id,
            "name": "Chat",
            "source": {
                "id": self.source_id
            },
            "session": {
                "id": self.chat_id,
                "chat": {
                    "ttl": self.chat_ttl
                },
            },
            "entities": self.entities,
            "relation": self.chats
        })

    @staticmethod
    def get_references() -> Tuple[InstanceLink, InstanceLink, InstanceLink]:
        observer = InstanceLink.create('observer')
        person = InstanceLink.create('person')
        agent = InstanceLink.create('agent')

        return observer, person, agent
