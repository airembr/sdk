import json
from datetime import datetime

from durable_dot_dict.dotdict import DotDict
from pydantic import ValidationError

from sdk.airembr.logging.log_handler import get_logger
from sdk.airembr.model.entity import Entity
from sdk.airembr.model.instance import Instance
from sdk.airembr.model.instance_link import InstanceLink
from sdk.airembr.model.observation import Observation, ObservationEntity, ObservationRelation, ObservationSemantic, \
    ObservationMetaContext, ObservationApp, ObservationOs, ObservationDevice, ObservationLocation, \
    ObservationDeviceGpu, ObservationPlace, ObservationCountry
from sdk.airembr.model.session import Session
from sdk.airembr.service.time.time import now_in_utc

logger = get_logger(__name__)


def _create_link(id, kind):
    return f"{kind}-{id[:16]}"

def convert_record_to_observation(flat: DotDict) -> Observation:
    def safe_json(value):
        try:
            return json.loads(value) if isinstance(value, str) and value.startswith('{') else value
        except Exception:
            return value

    def make_instance(kind: str | None, role: str | None, id_: str | None, actor=False) -> Instance | None:
        """
        Construct Instance like '*kind:role#id' (or without * if not actor)
        """
        if not kind:
            return None

        parts = []
        if actor:
            parts.append('*')
        parts.append(kind)
        if role:
            parts.append(f":{role}")
        if id_:
            parts.append(f"#{id_}")
        return Instance("".join(parts))

    # --- Entities ---
    entities = {}
    for prefix in ['actor', 'object']:
        id_ = flat.get(f'{prefix}.id')

        if not id_:
            # Skip abstract
            continue

        kind = flat.get(f'{prefix}.type')
        role = flat.get(f'{prefix}.role')
        actor_flag = (prefix == 'actor')

        instance = make_instance(kind, role, id_, actor=actor_flag)

        traits = safe_json(flat.get(f'{prefix}.traits', {}))
        part_of_id = flat.get_or_none(f'{prefix}.part_of.id')
        part_of_kind = flat.get_or_none(f'{prefix}.part_of.kind')
        is_a_id = flat.get_or_none(f'{prefix}.is_a.id')
        is_a_kind = flat.get_or_none(f'{prefix}.is_a.kind')

        entity = ObservationEntity(
            instance=instance,
            part_of=make_instance(part_of_kind, None, part_of_id) if part_of_id else None,
            is_a=make_instance(is_a_kind, None, is_a_id) if is_a_id else None,
            traits=traits or {}
        )

        entities[InstanceLink.create(_create_link(id_, 'ref'))] = entity

    # --- Relation ---
    relation = ObservationRelation(
        id=flat.get('rel.id'),
        label=flat.get('rel.label'),
        type=flat.get('rel.type', 'event'),
        observer=InstanceLink.create(_create_link(flat.get('actor.id'), 'ref')),
        actor=InstanceLink.create(_create_link(flat.get('actor.id'), 'ref')) if flat.get('actor.id') else None,
        objects=InstanceLink.create(_create_link(flat.get('object.id'), 'ref'))if flat.get('object.id') else None,
        traits=safe_json(flat.get('rel.traits', {})),
        semantic=ObservationSemantic(
            summary=flat.get_or_none('semantic.summary'),
            description=flat.get_or_none('semantic.description'),
            context=flat.get_or_none('semantic.context')
        ),
        ts=flat.get('metadata.time.create', now_in_utc()),
        order=flat.get_or_none('metadata.order')
    )

    # --- Metadata ---
    metadata = ObservationMetaContext(
        application=ObservationApp(
            agent=flat.get_or_none("app.agent") or "unknown/1.0",
            name=flat.get_or_none("app.name"),
            version=flat.get_or_none("app.version"),
            type_id=flat.get_or_none("app.type_id"),
            language=safe_json(flat.get_or_none("app.language")),
            aux=safe_json(flat.get_or_none("app.aux")),
        ),
        os=ObservationOs(
            type_id=flat.get_or_none("os.type_id"),
            name=flat.get_or_none("os.name"),
            version=flat.get_or_none("os.version"),
            platform=flat.get_or_none("os.platform"),
            aux=safe_json(flat.get_or_none("os.aux")),
        ),
        device=ObservationDevice(
            id=flat.get_or_none("device.id"),
            type_id=flat.get_or_none("device.type_id"),
            name=flat.get_or_none("device.name"),
            brand=flat.get_or_none("device.brand"),
            model=flat.get_or_none("device.model"),
            ip=flat.get_or_none("device.ip"),
            touch=flat.get_or_none("device.touch"),
            mobile=flat.get_or_none("device.mobile"),
            tablet=flat.get_or_none("device.tablet"),
            resolution=flat.get_or_none("device.resolution"),
            color_depth=flat.get_or_none("device.color_depth"),
            orientation=flat.get_or_none("device.orientation"),
            gpu=ObservationDeviceGpu(
                name=flat.get_or_none("device.gpu.name"),
                vendor=flat.get_or_none("device.gpu.vendor"),
            ),
            aux=safe_json(flat.get_or_none("device.aux")),
        ),
        location=ObservationLocation(
            type_id=flat.get_or_none("location.type_id"),
            place=ObservationPlace(
                name=flat.get_or_none("location.place.name"),
                type=flat.get_or_none("location.place.type"),
            ) if (
                    flat.get_or_none("location.place.name")
                    or flat.get_or_none("location.place.type")
            ) else None,
            country=ObservationCountry(
                name=flat.get_or_none("location.country.name"),
                code=flat.get_or_none("location.country.code"),
            ) if (
                    flat.get_or_none("location.country.name")
                    or flat.get_or_none("location.country.code")
            ) else None,
            city=flat.get_or_none("location.city"),
            county=flat.get_or_none("location.county"),
            postal=flat.get_or_none("location.postal"),
            latitude=flat.get_or_none("location.latitude"),
            longitude=flat.get_or_none("location.longitude"),
        ),
    )

    # --- Assemble Observation ---
    observation = Observation(
        id=flat.get_or_none('observation.id'),
        name=flat.get_or_none('observation.name'),
        aspect=flat.get_or_none('aspect'),
        source=Entity(id=flat.get('source.id')),
        session=Session(id=flat.get('session.id')),
        entities=entities,
        relation=[relation],
        metadata=metadata
    )

    return observation


def yield_records_as_observations(records):
    for record in records:
        try:
            yield convert_record_to_observation(record)
        except ValidationError as e:
            logger.warning(f"Error while converting record to observation. Reason: {str(e)}")