import hashlib
from datetime import datetime
from enum import Enum
from typing import Optional, List, Any, Dict, Generator, Set, Union, Tuple
from uuid import uuid4
from hashlib import md5

from durable_dot_dict.dotdict import DotDict
from pydantic import BaseModel, RootModel, model_validator, Field, PrivateAttr

from airembr.sdk.model.entity import Entity
from airembr.sdk.model.identification_id import IdentificationId
from airembr.sdk.model.instance import Instance
from airembr.sdk.model.instance_link import InstanceLink
from airembr.sdk.model.session import Session
from airembr.sdk.service.sementic import render_description
from airembr.sdk.service.text.cleanup import _clean_value
from airembr.sdk.service.time.time import now_in_utc
from airembr.sdk.model.named_entity import NamedEntity


class ObservationMeasurement(NamedEntity):
    value: float


class ObservationCollectConsent(BaseModel):
    allow: bool


class ObservationConsents(ObservationCollectConsent):
    granted: Set[str]


class EntityIdentification(BaseModel):
    properties: List[str]  # List of trait paths to use as base for identification
    strict: Optional[bool] = True  # Means: All properties must be present in traits to identify entity
    values_only: Optional[bool] = False  # Means: Hash only values of properties

    @staticmethod
    def by(properties: List[str]) -> 'EntityIdentification':
        return EntityIdentification(properties=properties, strict=False, values_only=True)

    def as_all_properties(self) -> 'EntityIdentification':
        self.strict = False
        return self

    def to_comma_separated_value(self) -> str:
        return ",".join(self.properties)


class ObservationEntity(BaseModel):
    instance: Instance = Field(..., description="Entity instance.")
    identification: Optional[EntityIdentification] = Field(None,
                                                           description="Way how the entity is identified. None is undefined.")

    label: Optional[str] = None
    part_of: Optional[Instance] = None
    is_a: Optional[Instance] = None
    has_a: Optional[List[Instance]] = None

    traits: Optional[dict] = {}
    state: Optional[Dict[str, InstanceLink]] = {}

    consents: Optional[ObservationCollectConsent] = None

    # Reference of this entity in observation
    _ref: InstanceLink = PrivateAttr(default_factory=InstanceLink)
    # Identification ID
    _iid: Optional[IdentificationId] = PrivateAttr(None)

    def __init__(self, **data):
        super().__init__(**data)
        self._ref = InstanceLink.create()
        # MUST BE LAST
        self._iid = self._resolve_id_from_properties()

        if self.instance.is_abstract():
            # If is abstract set instance id as identification ID
            if self.identification is not None:
                # We care about identification but forgot to set Instance ID
                if self._iid.is_empty():  # Empty when could not identify entity
                    # Abstract (No ID delivered in Instance)
                    # Not identified
                    # We care about identification (identification is set)
                    # Set random instance ID
                    self.instance = Instance.type(self.instance.kind, str(uuid4()))

                else:
                    # Abstract (No ID delivered in Instance) but identified
                    self.instance = Instance.type(self.instance.kind, self._iid.iid)

    def link(self, reference=None) -> InstanceLink:
        return reference if InstanceLink.create(reference) else self._ref

    @property
    def ref(self) -> InstanceLink:
        return self._ref

    @property
    def iid(self) -> Optional[IdentificationId]:
        return self._iid

    def has_iid(self) -> bool:
        return self._iid is not None and self._iid.iid is not None

    def _yield_traits_from_properties(self):
        for trait_path in self.identification.properties:
            if trait_path in self.traits:
                if self.identification.values_only:
                    yield self.traits[trait_path]
                    continue
                yield trait_path, self.traits[trait_path]

    def _resolve_id_from_properties(self) -> IdentificationId:

        if self.identification is None:
            return IdentificationId()

        if not self.identification.properties:
            return IdentificationId()  # No properties defined, nothing to do here.

        # Try to revolve id from properties
        hash_base = list(self._yield_traits_from_properties())

        if len(hash_base) == 0:
            # Not properties in traits to identify entity
            return IdentificationId()

        if self.identification.strict and len(hash_base) != len(self.identification.properties):
            # Not all properties in traits to identify entity
            return IdentificationId()

        hash_base = sorted(hash_base)
        hash_base = f"{self.instance.kind}:{hash_base}"

        return IdentificationId(iid=hashlib.md5(hash_base.encode()).hexdigest(),
                                type=self.identification.to_comma_separated_value())

    def is_consent_granted(self) -> bool:
        if self.consents is None:
            return True
        return self.consents.allow

    def __str__(self):
        if self.traits:
            converted = [f'{key}: {value}' for key, value in DotDict(self.traits).flat().items()]
            if self.instance.is_abstract():
                return f"{self.instance.kind} ({', '.join(converted)})"
            return f"{self.instance.kind} (id={self.instance.id}, {', '.join(converted)})"
        return self.instance.label()

    @staticmethod
    def init(instance: Instance, **kwargs) -> 'ObservationEntity':
        return ObservationEntity(instance=instance, **kwargs)


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

    def render(self, actor_link, object_link, observation) -> tuple[str, str, str]:
        summary, description, context = None, None, None
        if self.summary:
            summary = render_description(self.summary,
                                         actor_link,
                                         object_link,
                                         observation)
        if self.description:
            description = render_description(self.description,
                                             actor_link,
                                             object_link,
                                             observation)
        if self.context:
            context = render_description(self.context,
                                         actor_link,
                                         object_link,
                                         observation)
        return summary, description, context

    def is_empty(self):
        return self.summary is None and self.description is None and self.context is None


class ObservationRelation(BaseModel):
    id: Optional[str] = None
    ts: Optional[datetime] = None
    order: Optional[int] = None
    actor: Optional[Union[List[InstanceLink], InstanceLink, List[ObservationEntity], ObservationEntity]] = None
    actor_label: Optional[str] = None
    type: Optional[str] = 'fact'
    label: str
    semantic: Optional[ObservationSemantic] = None
    objects: Optional[Union[List[InstanceLink], InstanceLink, List[ObservationEntity], ObservationEntity]] = None
    traits: Optional[dict] = None
    context: Optional[List[InstanceLink]] = []
    tags: Optional[list] = []
    timer: Optional[ObservationTimer] = None
    subjective: Optional[bool] = True  # Is information subjective?

    consents: Optional[ObservationCollectConsent] = None

    def __init__(self, /, **data: Any):
        # create if none
        if data.get('id', None) is None:
            data['id'] = str(uuid4())
        if data.get('ts', None) is None:
            data['ts'] = now_in_utc()

        if isinstance(data.get('observer', None), ObservationEntity):
            data['observer'] = data['observer'].ref

        _actor = data.get('actor', None)
        if _actor:
            if isinstance(_actor, ObservationEntity):
                data['actor'] = _actor.ref
            elif isinstance(_actor, list) and isinstance(_actor[0], ObservationEntity):
                data['actor'] = [item.ref for item in _actor]

        _objects = data.get('objects', None)
        if _objects:
            if isinstance(_objects, list) and isinstance(_objects[0], ObservationEntity):
                data['objects'] = [item.ref for item in _objects]
            elif isinstance(_objects, ObservationEntity):
                data['objects'] = _objects.ref

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
    
    def semantic_summary(self) -> list[str]:
        lines =[]
        if self.semantic:
            lines.append(f"Time: {self.ts}")
            if self.semantic.summary:
                lines.append(f"Summary: {_clean_value(self.semantic.summary)}")
            if self.semantic.description:
                lines.append(f"Description: {_clean_value(self.semantic.description)}")
            if self.semantic.context:
                lines.append(f"Context: {_clean_value(self.semantic.context)}")
            return lines
        return []


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
    trace_id: Optional[str] = None


class EntityRefs(RootModel[Union[Tuple, Dict[InstanceLink, ObservationEntity]]]):

    @model_validator(mode="before")
    @classmethod
    def normalize_input(cls, value):
        # Case 1: already a dict → keep as-is
        if isinstance(value, dict):
            return value

        # Case 2: a set (or any iterable) of entities
        if isinstance(value, (set, tuple)):
            return {entity.ref: entity for entity in value}

        raise TypeError(
            "EntityRefs must be initialized with a dict or a set of ObservationEntity"
        )

    def get(self, link: InstanceLink) -> Optional[ObservationEntity]:
        return self.root.get(link, None)

    def add(self, link: InstanceLink, entity: ObservationEntity):
        self.root[link] = entity

    def index(self) -> Dict[str, ObservationEntity]:
        return self.root

    def list(self):
        return self.root.values()

    def items(self):
        return self.root.items()

    def links(self):
        return self.root.keys()


class EntityIndex(BaseModel):
    root: Dict[str, dict] = Field(default_factory=dict)

    def get(self, link: InstanceLink) -> Optional[dict]:
        return self.root.get(link, None)


class Observation(BaseModel):
    id: Optional[str] = Field(None, description="Observation id")
    observer: InstanceLink = Field(..., description="Observation observer entity.")
    name: Optional[str] = Field(None, description="Observation name")
    source: Entity = Field(..., description="Observation source entity.")
    session: Optional[Session] = Field(Session(), description="Observation session entity.")
    entities: Optional[EntityRefs] = EntityRefs({})
    relation: List[ObservationRelation]  # Should be relation
    context: Optional[Union[List[InstanceLink], InstanceLink]] = None
    metadata: Optional[ObservationMetaContext] = None
    consents: Optional[ObservationConsents] = None
    aux: Optional[dict] = None  # Put here all the additional dimensions

    _index_entities: Optional[EntityIndex] = PrivateAttr(None)

    def __init__(self, /, **data: Any):
        super().__init__(**data)
        if not self.id:
            self.id = f"anon-{str(uuid4())}"

        self._validate_links()

    # @model_validator(mode="after")
    # def inject_ts_into_relations(self):
    #     for rel in self.relation:
    #         if rel.ts is None:
    #             rel.ts = self.id
    #     return self

    def _validate_links(self):
        # Validate observer link
        if not self.get_observer():
            raise ValueError(
                f"Observer link {self.observer} not found in entities, but referenced as observer.")

        # Validate entities links
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

    def get_observer(self) -> Optional[ObservationEntity]:
        return self.entities.get(self.observer)

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

    def get_indexed_entities(self) -> EntityIndex:
        if self._index_entities is None:
            _indexed_entities = {}
            for link, entity in self.entities.root.items():  # type: ObservationEntity

                instance = entity.instance
                traits = entity.traits
                state = entity.state

                try:
                    entity_id = instance.resolve_id(properties=traits, generate_id=True)
                except ValueError as e:
                    entity_id = str(uuid4())

                _indexed_entities[link] = {
                    "id": entity_id,
                    "instance": instance,
                    "traits": traits,
                    "state": state
                }

            self._index_entities = EntityIndex(root=_indexed_entities)
        return self._index_entities


class IdPath:

    def __init__(self, property: str, hash: bool):
        self.hash = hash
        self.property = property


class Init:
    def __init__(self, instance: str, id: Optional[str] = None, auto: bool = False):
        if id is None and auto:
            id = str(uuid4())

        if id is not None:
            instance = f"{instance}  #{id}"

        self.instance = Instance(instance)
        self.identification = None
        self._id_path: Optional[IdPath] = None

    def traits(self, traits: Optional[dict] = None,
               state: Optional[Dict[str, InstanceLink]] = None) -> ObservationEntity:
        if traits is None:
            traits = {}

        if self._id_path:
            instance_string = self.instance.kind
            _id = traits.get(self._id_path.property, None)
            if _id:
                if self._id_path.hash:
                    instance_string += f" #{md5(_id.encode()).hexdigest()}"
                else:
                    instance_string += f" #{_id.replace(' ', '-').lower()}"
        else:
            instance_string = str(self.instance)

        return ObservationEntity(
            instance=Instance(instance_string),
            traits=traits,
            identification=self.identification,
            state=state
        )

    def identified_by(self, properties: List[str]) -> 'Init':
        self.identification = EntityIdentification.by(properties)
        return self

    def id(self, property: str, hashed: bool = False) -> 'Init':
        self._id_path = IdPath(property, hashed)
        return self
