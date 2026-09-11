import json
from typing import Optional, Tuple

from pararun.model.status import DispatchStatus

from airembr.model.system.headers import Headers
from airembr.model.api.request.observation import Observation
from airembr.sdk.service.dict_traverser import DictTraverser
from airembr.sdk.service.dot_accessor import DotAccessor
from airembr.system.command.collect.observations import collect_observations
from airembr.system.process.sourcing.source_validation import validate_source


async def collect_webhook_observation(source_id: str,
                                      params: dict,
                                      body,
                                      headers: Headers) -> Tuple[Optional[dict], DispatchStatus | None]:
    headers['x-bridge'] = 'webhook'

    source = await validate_source(headers, source_id, allowed_bridges=['webhook'])

    dot = DotAccessor(
        payload={
            "params": params,
            "body": body
        }
    )
    converter = DictTraverser(dot)
    mapping = json.loads(source.config.get('mapping', 'null'))
    observation_dict = converter.reshape(mapping)
    observation = Observation(**observation_dict)

    return await collect_observations([observation], headers)
