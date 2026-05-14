from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Set, Union, Tuple

from pydantic import BaseModel, RootModel, Field, PrivateAttr

from airembr_sdk.model.core.instance import Instance
from airembr_sdk.model.interface.i_identification_id import IdentificationId
from airembr_sdk.model.core.instance_link import InstanceLink
from airembr_sdk.model.interface.i_entity import IEntity
from airembr_sdk.model.interface.i_session import ISession


class IObservationCollectConsent(BaseModel):
    allow: bool


class IObservationConsents(IObservationCollectConsent):
    granted: Set[str]


class IEntityIdentification(BaseModel):
    properties: List[str]  # List of trait paths to use as base for identification
    strict: Optional[bool] = True  # Means: All properties must be present in traits to identify entity
    values_only: Optional[bool] = False  # Means: Hash only values of properties


class IObservationEntity(BaseModel):
    instance: Instance = Field(..., description="Entity instance.")
    identification: Optional[IEntityIdentification] = Field(None,
                                                            description="Way how the entity is identified. None is undefined.")

    label: Optional[str] = None
    part_of: Optional[Instance] = None
    is_a: Optional[Instance] = None
    has_a: Optional[List[Instance]] = None

    traits: Optional[dict] = {}
    state: Optional[Dict[str, InstanceLink]] = {}

    consents: Optional[IObservationCollectConsent] = None

    # Reference of this entity in observation
    _ref: InstanceLink = PrivateAttr(default_factory=InstanceLink)

    # Identification ID
    _iid: Optional[IdentificationId] = PrivateAttr(None)


class IStatusEnum(str, Enum):
    on = "on"
    off = "off"
    pending = "pending"


class IObservationTimer(IEntity):
    status: IStatusEnum
    timeout: Optional[int] = None
    event: Optional[str] = None


class ISemantic(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    ner: Optional[bool] = False  # Named Entity Description


class IObservationRelation(BaseModel):
    id: Optional[str] = None
    ts: Optional[datetime] = None
    order: Optional[int] = None
    actor: Optional[Union[List[InstanceLink], InstanceLink, List[IObservationEntity], IObservationEntity]] = None
    actor_label: Optional[str] = None
    type: Optional[str] = 'fact'
    label: str
    text: Optional[ISemantic] = ISemantic()
    objects: Optional[Union[List[InstanceLink], InstanceLink, List[IObservationEntity], IObservationEntity]] = None
    traits: Optional[dict] = None
    context: Optional[List[InstanceLink]] = []
    tags: Optional[list] = []
    timer: Optional[IObservationTimer] = None
    subjective: Optional[bool] = True  # Is information subjective?

    consents: Optional[IObservationCollectConsent] = None


class IEntityRefs(RootModel[Union[Tuple, Dict[InstanceLink, IObservationEntity]]]):
    pass


class IEntityIndex(BaseModel):
    root: Dict[str, dict] = Field(default_factory=dict)


class IObservation(BaseModel):
    id: Optional[str] = Field(None, description="Observation id")
    insert_ts: Optional[datetime] = Field(None, description="Observation insert timestamp")
    create_ts: Optional[datetime] = Field(None, description="Observation create timestamp")
    label: Optional[str] = Field(None, description="Observation label")
    traits: Optional[dict] = Field(None, description="Observation traits")
    text: ISemantic = Field(ISemantic(), description="Observation semantics")
    observer: InstanceLink = Field(..., description="Observation observer entity.")
    source: IEntity = Field(..., description="Observation source entity.")
    session: Optional[ISession] = Field(ISession(), description="Observation session entity.")
    entities: Optional[IEntityRefs] = IEntityRefs({})
    relation: Optional[List[IObservationRelation]] = []
    context: Optional[Union[List[InstanceLink], InstanceLink]] = None
    consents: Optional[IObservationConsents] = None
    aux: Optional[dict] = None  # Put here all the additional dimensions

    _index_entities: Optional[IEntityIndex] = PrivateAttr(None)
