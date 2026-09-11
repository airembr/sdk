from typing import Optional, Tuple

from pararun.model.status import DispatchStatus

from airembr.model.system.entity import Entity
from airembr.model.system.headers import Headers
from airembr.model.api.request.observation import Observation, ObservationRelation
from airembr.model.payload.simplified_observation import SimplifiedObservation
from airembr.system.command.collect.observations import collect_observations
from airembr_sdk.core.date import now_in_utc


async def collect_simplified_observation(name: str,
                                         id: Optional[str],
                                         source_id: str,
                                         payload: SimplifiedObservation,
                                         headers: Headers) -> Tuple[Optional[dict], DispatchStatus | None]:
    entities = {}
    if payload.actor:
        entities["actor-1"] = payload.actor.model_dump(mode='json', exclude_none=True, exclude={"role": ...})
    if payload.object:
        entities["object-1"] = payload.object.model_dump(mode='json', exclude_none=True, exclude={"role": ...})

    observation = Observation(
        id=id,
        name=name,
        source=Entity(id=source_id),
        entities=entities,
        relation=[
            ObservationRelation(
                ts=now_in_utc(),
                actor='actor-1' if payload.actor.role is None else f"actor-1:{payload.actor.role}",
                type=payload.relation.type,
                label=payload.relation.label,
                objects=['object-1'],
                traits=payload.relation.traits,
            )
        ],
        metadata=payload.metadata
    )

    return await collect_observations([observation], headers)
