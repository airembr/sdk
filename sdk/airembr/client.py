from datetime import datetime
from typing import Optional
from uuid import uuid4

from sdk.airembr.model.observation import Observation
from sdk.airembr.service.api.sync_api import SyncApi
from sdk.airembr.service.time.time import now_in_utc


class AiRembrChatClient:

    def __init__(self,
                 api: str,
                 source_id: str,
                 person_instance: str,
                 chat_id: str, chat_ttl: int = 60 * 60,
                 agent_instance: Optional[str] = 'agent #agent',
                 agent_traits=None,
                 person_traits=None,
                 tenant_id: Optional[str] = None
                 ):

        if agent_traits is None:
            agent_traits = {}

        if person_traits is None:
            person_traits = {}

        self.api = api
        self.person_instance = person_instance
        self.agent_traits = agent_traits
        self.agent_instance = agent_instance
        self.chat_ttl = chat_ttl
        self.source_id = source_id
        self.chat_id = chat_id
        self.chats = []
        self.person_traits = person_traits

    def person(self, message: str, date: Optional[datetime] = None, fact_label: Optional[str] = 'messaged'):
       self.chat(message, "person", date, fact_label)

    def agent(self, message: str, date: Optional[datetime] = None, fact_label: Optional[str] = 'messaged'):
       self.chat(message, "agent", date, fact_label)

    def chat(self, message: str, by: str, date: Optional[datetime] = None, fact_label: Optional[str] = 'messaged'):
        chat = {
            "ts": now_in_utc() if date is None else date,
            "type": "chat",
            "label": fact_label,
            "actor": by,
            "objects": "person" if by != "person" else "agent",
            "semantic": {
                "summary": message
            }
        }
        self.chats.append(chat)

    def remember(self,
                 realtime: Optional[str] = None,
                 skip: Optional[str] = None,
                 response: bool = True,
                 context: Optional[str] = None):

        if self.chats:
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
                "entities": {
                    "agent": {
                        "instance": self.agent_instance,
                        "traits": self.agent_traits,
                    },
                    "person": {
                        "instance": self.person_instance,
                        "traits": self.person_traits
                    }

                },
                "relation": self.chats
            })

            transport = SyncApi(self.api, realtime, skip, response, context)
            payload = payload.model_dump(mode="json")

            return transport.remember(
                [payload]
            )
