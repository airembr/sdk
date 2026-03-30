import json

from durable_dot_dict.dotdict import DotDict
from pydantic import ValidationError

from airembr.sdk.logging.log_handler import get_logger
from airembr.sdk.model.entity import Entity
from airembr.sdk.model.instance import Instance
from airembr.sdk.model.instance_link import InstanceLink
from airembr.sdk.model.observation import Observation, ObservationEntity, ObservationRelation, ObservationSemantic
from airembr.sdk.model.session import Session
from airembr.sdk.service.time.time import now_in_utc

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

        actor_flag = (prefix == 'actor')

        id_ = flat.get_or_none(f'{prefix}.id') or flat.get_or_none(f'{prefix}.pk')
        kind = flat.get_or_none(f'{prefix}.type')
        role = flat.get_or_none(f'{prefix}.role')
        instance = make_instance(kind, role, id_, actor=actor_flag)

        if not instance:
            continue

        if actor_flag and (not id_ or not kind):
            # Skip abstract actor
            continue

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

    actor_id = flat.get_or_none('actor.id')
    actor_pk = flat.get_or_none('actor.pk')
    if actor_id is not None:
        actor_instance = InstanceLink.create(_create_link(actor_id, 'ref'))
    elif actor_pk is not None:
        actor_instance = InstanceLink.create(_create_link(actor_pk, 'ref'))
    else:
        actor_instance = None

    # --- Relation ---
    relation = ObservationRelation(
        id=flat.get('rel.id'),
        label=flat.get('rel.label'),
        type=flat.get('rel.type', 'event'),
        actor=actor_instance,
        objects=InstanceLink.create(_create_link(flat.get('object.id'), 'ref')) if flat.get('object.id', None) else None,
        traits=safe_json(flat.get('rel.traits', {})),
        semantic=ObservationSemantic(
            summary=flat.get_or_none('semantic.summary'),
            description=flat.get_or_none('semantic.description'),
            context=flat.get_or_none('semantic.context')
        ),
        ts=flat.get('metadata.time.create', now_in_utc()),
        order=flat.get_or_none('metadata.order')
    )

    print(actor_instance, flat)
    # --- Assemble Observation ---
    observation = Observation(
        id=flat.get_or_none('observation.id'),
        name=flat.get_or_none('observation.name'),
        aspect=flat.get_or_none('aspect'),
        source=Entity(id=flat.get('source.id')),
        session=Session(id=flat.get('session.id')),
        observer=actor_instance,
        entities=entities,
        relation=[relation],
    )

    return observation


def yield_records_as_observations(records):
    for record in records:
        try:
            yield convert_record_to_observation(record)
        except ValidationError as e:
            logger.warning(f"Error while converting record to observation. Reason: {str(e)}")