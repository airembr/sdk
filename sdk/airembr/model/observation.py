import hashlib
from datetime import datetime
from enum import Enum
from typing import Optional, List, Any, Dict, Generator, Set, Union
from uuid import uuid4

from durable_dot_dict.dotdict import DotDict
from pydantic import BaseModel, RootModel

from sdk.airembr.model.entity import Entity
from sdk.airembr.model.instance import Instance
from sdk.airembr.model.instance_link import InstanceLink
from sdk.airembr.model.session import Session
from sdk.airembr.service.sementic import render_description
from sdk.airembr.service.time.time import now_in_utc
from sdk.airembr.model.named_entity import NamedEntity


class ObservationMeasurement(NamedEntity):
    value: float


class ObservationCollectConsent(BaseModel):
    allow: bool


class ObservationConsents(ObservationCollectConsent):
    granted: Set[str]


class ObservationEntity(BaseModel):
    instance: Instance

    part_of: Optional[Instance] = None
    is_a: Optional[Instance] = None
    has_a: Optional[List[Instance]] = None

    traits: Optional[dict] = {}

    consents: Optional[ObservationCollectConsent] = None

    def is_consent_granted(self) -> bool:
        if self.consents is None:
            return True
        return self.consents.allow

    def __str__(self):
        if self.traits:
            converted = [f'{key}: {value}' for key, value in DotDict(self.traits).flat().items()]
            return f"{self.instance.label()} ({', '.join(converted)})"
        return self.instance.label()


class StatusEnum(str, Enum):
    on = "on"
    off = "off"
    pending = "pending"


class ObservationTimer(Entity):
    status: StatusEnum
    timeout: Optional[int] = None
    event: Optional[str] = None

    def __init__(self, /, **data: Any):
        super().__init__(**data)
        if self.status != StatusEnum.off:
            if self.timeout is None:
                raise ValueError(
                    "Error. Timer without time-out. Time-out must be set for timers that are on or pending.")
            if self.event is None:
                raise ValueError(
                    "Error. Timer without event type. Event must be set for timers that are on or pending.")


class ObservationSemantic(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    context: Optional[str] = None

    def render(self, actor_link, object_link, observation):
        if self.summary:
            self.summary = render_description(self.summary,
                                              actor_link,
                                              object_link,
                                              observation)
        if self.description:
            self.description = render_description(self.description,
                                                  actor_link,
                                                  object_link,
                                                  observation)
        if self.context:
            self.context = render_description(self.context,
                                              actor_link,
                                              object_link,
                                              observation)


class ObservationRelation(BaseModel):
    id: Optional[str] = None
    ts: Optional[datetime] = None
    actor: Optional[Union[List[InstanceLink], InstanceLink]] = None
    type: Optional[str] = 'fact'
    label: str
    semantic: Optional[ObservationSemantic] = None
    objects: Optional[Union[List[InstanceLink], InstanceLink]] = None
    traits: Optional[dict] = None
    context: Optional[List[InstanceLink]] = []
    tags: Optional[list] = []
    timer: Optional[ObservationTimer] = None

    consents: Optional[ObservationCollectConsent] = None

    def __init__(self, /, **data: Any):
        # create if none
        if data.get('id', None) is None:
            data['id'] = str(uuid4())
        if data.get('ts', None) is None:
            data['ts'] = now_in_utc()
        super().__init__(**data)

        if self.objects:
            self.objects = list(set(self.objects)) if isinstance(self.objects, list) else [self.objects]
        else:
            self.objects = []

    def get_actor(self) -> Optional[InstanceLink]:
        if not self.actor:
            return None
        return self.actor

    def get_objects(self) -> Generator[InstanceLink, None, None]:
        if isinstance(self.objects, list):
            for link in self.objects:
                yield link

    def is_consent_granted(self) -> bool:
        if self.consents is None:
            return True
        return self.consents.allow

    def has_sematic_part(self) -> bool:
        return self.semantic is not None

    def __str__(self):
        if self.traits:
            converted = [f'{key}: {value}' for key, value in DotDict(self.traits).flat().items()]
            return f"{self.label}:{self.type} ({', '.join(converted)})"
        return self.label


class ObservationCountry(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None

    def __eq__(self, other):
        return self.name == other.name and self.code == other.code


class ObservationPlace(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None


class ObservationLocation(BaseModel):
    type_id: Optional[str] = None
    place: Optional[ObservationPlace] = None
    country: Optional[ObservationCountry] = None
    city: Optional[str] = None
    county: Optional[str] = None
    postal: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ObservationApp(BaseModel):
    agent: Optional[str] = "unknown/1.0"
    name: Optional[str] = None
    version: Optional[str] = None
    type_id: Optional[str] = None
    language: Optional[List[str]] = None

    aux: Optional[dict] = None


class ObservationOs(BaseModel):
    type_id: Optional[str] = None
    name: Optional[str] = None
    version: Optional[str] = None
    platform: Optional[str] = None
    aux: Optional[dict] = None


class ObservationDeviceGpu(BaseModel):
    name: Optional[str] = None
    vendor: Optional[str] = None


class ObservationDevice(BaseModel):
    id: Optional[str] = None
    type_id: Optional[str] = None
    name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    ip: Optional[str] = None
    type: Optional[Entity] = None
    touch: Optional[bool] = None
    mobile: Optional[bool] = None
    tablet: Optional[bool] = None
    resolution: Optional[str] = None
    color_depth: Optional[int] = None
    orientation: Optional[str] = None
    gpu: Optional[ObservationDeviceGpu] = None

    aux: Optional[dict] = None

    def get_hashed_id(self) -> Optional[str]:
        if self.id:
            return hashlib.md5(self.id.encode()).hexdigest()
        return None


class ObservationMetaContext(BaseModel):
    application: Optional[ObservationApp] = None
    device: Optional[ObservationDevice] = None
    os: Optional[ObservationOs] = None
    location: Optional[ObservationLocation] = None


class EntityRefs(RootModel[Dict[str, ObservationEntity]]):

    def get(self, link) -> Optional[ObservationEntity]:
        return self.root.get(link, None)

    def add(self, link, entity: ObservationEntity):
        self.root[link] = entity

    def index(self) -> Dict[str, ObservationEntity]:
        return self.root

    def list(self):
        return self.root.values()

    def items(self):
        return self.root.items()

    def links(self):
        return self.root.keys()


class Observation(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    aspect: Optional[str] = None
    source: Entity
    session: Optional[Session] = Session()
    entities: Optional[EntityRefs] = EntityRefs({})
    relation: List[ObservationRelation]  # Should be relation
    context: Optional[Union[List[InstanceLink], InstanceLink]] = None
    metadata: Optional[ObservationMetaContext] = None
    consents: Optional[ObservationConsents] = None
    aux: Optional[dict] = None  # Put here all the additional dimensions

    def __init__(self, /, **data: Any):

        if not isinstance(data.get('entities', {}), dict):
            raise ValueError(
                "Entities in observation must be a dictionary, with a key as reference and value as ObservationEntity object.")

        super().__init__(**data)
        if not self.id:
            self.id = f"anon-{str(uuid4())}"

        self._validate_links()

    def _validate_links(self):
        links = self.entities.links()
        for relation in self.relation:
            objects = list(relation.get_objects())
            for obj in objects:
                obj_link = obj.link
                if obj_link not in links:
                    raise ValueError(
                        f"Entity link {obj_link} not found in entities, but referenced in relation {objects} (label: {relation.label}).")

    def _index_entity_traits(self) -> Dict[str, dict]:
        return {link: observed_entity.traits for link, observed_entity in self.entities.root.items()}

    def is_consent_granted(self) -> bool:
        if self.consents is None:
            return True
        return self.consents.allow

    def get_consents(self) -> Optional[Set[str]]:
        if self.consents is None:
            return None
        return self.consents.granted

    def get_device(self) -> Optional[ObservationDevice]:
        if self.metadata and self.metadata.device:
            return self.metadata.device
        return None

    def get_application(self) -> Optional[ObservationApp]:
        if self.metadata and self.metadata.application:
            return self.metadata.application
        return None

    def get_os(self) -> Optional[ObservationOs]:
        if self.metadata and self.metadata.os:
            return self.metadata.os
        return None

    def get_location(self) -> Optional[ObservationLocation]:
        if self.metadata and self.metadata.location:
            return self.metadata.location
        return None

    def get_session_id(self, default=None) -> Optional[str]:
        if isinstance(self.session, Session):
            if self.session.id is None:
                return default
            return self.session.id

        return None

    def get_chat_ttl(self, default=2629746) -> Optional[int]:
        if isinstance(self.session, Session) and self.session.chat:
            if self.session.chat.ttl is None:
                return default
            return self.session.chat.ttl

        return 2629746  # Month

    def get_chat_compression_trigger(self, default=102400) -> Optional[int]:
        if isinstance(self.session, Session) and self.session.chat:
            if self.session.chat.compress_after is None:
                return default
            return self.session.chat.compress_after

        return 102400  # 100KB

    def _get_chat_ttl_type(self, default='keep') -> Optional[str]:
        if isinstance(self.session, Session) and self.session.chat:
            if self.session.chat.ttl_type is None:
                return default
            return self.session.chat.ttl_type

        return None

    def is_chat(self) -> bool:
        return isinstance(self.session, Session) and self.session.chat is not None

    def should_chat_ttl_be_overridden(self) -> bool:
        return self._get_chat_ttl_type() == 'override'

    def get_entities(self) -> List[str]:
        return [f"{link} -> {str(entity)}" for link, entity in self.entities.items()]
