from typing import List, Optional, Tuple

from airembr.model.system.header_schema import V_OBSERVATION
from pararun.model.status import DispatchStatus

from airembr.model.system.entity import Entity
from airembr.model.system.headers import Headers
from airembr.model.api.request.observation import Observation, ObservationEntity
from airembr.system.adapter.bigdata.big_data_adapter import bd_observation_adapter
from airembr.system.command.collect.errors import CollectorError
from airembr.system.command.collect.observations import collect_observations
from airembr_sdk.model.core.instance import Instance


async def add_entities_to_observation(observation_id: str,
                                      observer_type: str,
                                      observer_id: str,
                                      entities: List[ObservationEntity],
                                      headers: Headers) -> Tuple[Optional[dict], DispatchStatus | None]:

    observation_result = await bd_observation_adapter.load_observation_by_id(observation_id)
    if not observation_result:
        raise CollectorError(detail=f"Observation '{observation_id}' not found.", status_code=404)

    observation_rows = observation_result.list()
    if not observation_rows:
        raise CollectorError(detail=f"Observation '{observation_id}' not found.", status_code=404)

    # This endpoint should not save observation, only entities.
    if V_OBSERVATION in headers.get_skipped():
        headers.add_skipped(V_OBSERVATION)

    source_id = observation_rows[0].get("source_id")

    observer_entity = ObservationEntity(instance=Instance.type(observer_type, observer_id))

    observation = Observation(
        id=observation_id,
        observer=observer_entity.ref,
        source=Entity(id=source_id),
        entities=tuple(entities) + (observer_entity,),
        relation=[],
    )

    return await collect_observations([observation], headers)
