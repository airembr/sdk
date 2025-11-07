from datetime import datetime
from typing import Optional, Tuple
from uuid import uuid4

from sdk.airembr.model.instance_link import InstanceLink
from sdk.airembr.model.memory.conversation_memory import MemorySessions
from sdk.airembr.model.observation import Observation
from sdk.airembr.model.query.status import QueryStatus
from sdk.airembr.service.api.sync_api import SyncApi
from sdk.airembr.service.time.time import now_in_utc


def _create_object(by) -> str:
    return "person" if by != "person" else "agent"


class AiRembrChatClient:

    def __init__(self,
                 api: str,
                 source_id: str,
                 entities,
                 observer: InstanceLink,
                 chat_id: str, chat_ttl: int = 60 * 60,
                 tenant_id: Optional[str] = None
                 ):
        self.observer = observer
        self.entities = entities

        self.api = api
        self.chat_ttl = chat_ttl
        self.source_id = source_id
        self.chat_id = chat_id
        self.chats = []

    def chat(self, message: str, by: InstanceLink, date: Optional[datetime] = None,
             fact_label: Optional[str] = 'messaged'):
        chat = {
            "ts": now_in_utc() if date is None else date,
            "type": "chat",
            "label": fact_label,
            "observer": self.observer,
            "actor": by,
            "objects": InstanceLink.create(_create_object(by)),
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

        payload = Observation(**{
            "id": str(uuid4()),
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

        transport = SyncApi(self.api)
        payload = payload.model_dump(mode="json")

        return transport.remember(
            [payload],
            realtime, skip, response, context
        )

    @staticmethod
    def get_references() -> Tuple[InstanceLink, InstanceLink, InstanceLink]:
        observer = InstanceLink.create('observer')
        person = InstanceLink.create('person')
        agent = InstanceLink.create('agent')

        return observer, person, agent
