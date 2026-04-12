from collections import defaultdict
from datetime import datetime
from typing import Optional, Tuple, List, Union, Dict, Set
from uuid import uuid4

from airembr.sdk.model.entity import Entity
from airembr.sdk.model.fact import Relation
from airembr.sdk.model.instance import Instance
from airembr.sdk.model.instance_link import InstanceLink
from airembr.sdk.model.memory.conversation_memory import MemorySessions
from airembr.sdk.model.observation import Observation, ObservationEntity, ObservationRelation, Semantic
from airembr.sdk.model.query.status import QueryStatus
from airembr.sdk.model.session import Session, ChatSession
from airembr.sdk.service.remote.airembr_api import AirembrApi
from airembr.sdk.service.time.time import now_in_utc


def entity(type: str, traits: Optional[dict] = None, label: Optional[str] = None,
           id: Optional[str] = None) -> 'AiRembrChatEntity':
    return AiRembrChatEntity(
        entity=ObservationEntity(
            instance=Instance.type(type, id),
            label=label,
            traits=traits
        )
    )

def event(type: str, traits: Optional[dict] = None, label: Optional[str] = None):
    return AiRembrEvent(
        type=type,
        traits=traits,
        label=label
    )

class _Chats:
    def __init__(self):
        self._chats = defaultdict(list)

    def add(self, observation_id, chat):
        self._chats[observation_id].append(chat)

    def values(self):
        return self._chats.values()

    def list(self):
        for observation_id, chats in self._chats.items():
            yield observation_id, chats

    def __len__(self):
        return sum([len(item) for item in self._chats.values()])

class AiRembrEvent:

    def __init__(self, type: str, traits: Optional[dict] = None, label: Optional[str] = None):
        self.label = label
        self.traits = traits
        self.type = type

class AiRembrChatEntity:

    def __init__(self, entity: ObservationEntity):
        self.link: InstanceLink = InstanceLink.create()
        self.entity: ObservationEntity = entity

    def get_reference(self) -> Tuple[InstanceLink, ObservationEntity]:
        return self.link, self.entity


class AiRembrChatPeer:

    def __init__(self, client: 'AiRembrChatClient', observation: 'AirembrObservation', entity: AiRembrChatEntity):
        self.observation = observation
        self.client = client
        self.entity: AiRembrChatEntity = entity
        self.chats: _Chats = _Chats()

    def message(self, message: str,
                summary: Optional[str] = None,
                who: 'AiRembrChatPeer' = None,
                date: Optional[Union[datetime | str]] = None,
                label: Optional[str] = 'messaged'):
        if date is not None and isinstance(date, str):
            date = datetime.fromisoformat(date)

        chat = ObservationRelation(
            ts=now_in_utc() if date is None else date,
            type="chat",
            label=label,
            actor=self.entity.link,
            objects=[who.entity.link],
            semantic=Semantic(
                description=message,
                summary=summary
            )
        )

        self.chats.add(self.observation.observation_id, chat)

    def get_reference(self) -> Tuple[InstanceLink, ObservationEntity]:
        return self.entity.get_reference()


class AirembrChat:

    def __init__(self,
                 client: 'AiRembrChatClient',
                 observation: 'AirembrObservation',
                 chat_id: str,
                 chat_ttl: int = 60 * 60):
        self.observation = observation
        self.client = client
        self.chat_ttl = chat_ttl
        self.chat_id = chat_id
        self.peers: Set[AiRembrChatPeer] = set()
        self.entities: Set[AiRembrChatEntity] = set()

    def peer(self, entity: AiRembrChatEntity) -> AiRembrChatPeer:
        peer = AiRembrChatPeer(
            self.client,
            self.observation,
            entity
        )

        self.peers.add(peer)
        return peer

    def entity(self, entity: Union[AiRembrChatEntity, Set[AiRembrChatEntity]]):
        if isinstance(entity, set):
            self.entities.update(entity)
        else:
            self.entities.add(entity)

    def _yield_referenced_entites(self):
        for peer in self.peers:
            yield peer.get_reference()

        for entity in self.entities:
            yield entity.get_reference()

    def _yield_chat_observation(self):
        entities = {link: entity for link, entity in self._yield_referenced_entites()}
        print(1, entities)
        for peer in self.peers:
            for observation_id, chats in peer.chats.list():
                yield Observation(
                    id=observation_id,
                    name="Chat",
                    source=Entity(id=self.client.source_id),
                    session=Session(
                        id=self.chat_id,
                        chat=ChatSession(ttl=self.chat_ttl)
                    ),
                    observer=self.observation.observer_link,
                    entities=entities,
                    relation=chats
                )

    def remember(self,
                 realtime: Optional[str] = None,
                 skip: Optional[str] = None,
                 response: bool = True,
                 context: Optional[str] = None) -> Tuple[QueryStatus, MemorySessions]:

        chats = [len(peer.chats) > 0 for peer in self.peers]

        if not any(chats):
            return QueryStatus(404), MemorySessions({})

        transport = AirembrApi(self.client.api)
        payload = [observation.model_dump(mode="json") for observation in self._yield_chat_observation()]

        return transport.remember(
            payload,
            realtime, skip, response, context
        )


class AirembrObservation:

    def __init__(self, client, observer: AiRembrChatEntity, id: Optional[str] = None,
                 session_id: Optional[str] = None):
        self.client = client
        self.observation_id = id or str(uuid4())
        self.session_id = session_id or str(uuid4())
        self.observer_link = observer.link

    def chat(self,
             chat_id: str,
             chat_ttl: int = 60 * 60) -> AirembrChat:
        return AirembrChat(self.client, self, chat_id, chat_ttl)


class AiRembrChatClient:

    def __init__(self,
                 api: str,
                 source_id: str,

                 ):
        self.observation_id: Optional[str] = None
        self.session_id: Optional[str] = None
        self._observer: Optional[InstanceLink] = None

        self.api = api
        self.source_id = source_id
        self.chat_ttl: Optional[int] = None
        self.chat_id: Optional[str] = None

    def observation(self,
                    observer: AiRembrChatEntity,
                    id: Optional[str] = None,
                    session_id: Optional[str] = None) -> AirembrObservation:
        return AirembrObservation(self, observer, id, session_id)

    @staticmethod
    def get_references() -> Tuple[InstanceLink, InstanceLink, InstanceLink]:
        observer = InstanceLink.create('observer')
        person = InstanceLink.create('person')
        agent = InstanceLink.create('agent')

        return observer, person, agent
