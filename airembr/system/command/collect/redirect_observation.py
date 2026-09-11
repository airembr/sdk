import json

from airembr.model.system.entity import Entity
from airembr.model.system.header_schema import X_BRIDGE, X_CONTEXT, V_STAGING, V_PRODUCTION
from airembr.model.system.headers import Headers
from airembr.model.api.request.observation import Observation, ObservationRelation
from airembr.sdk.service.dict_traverser import DictTraverser
from airembr.sdk.service.dot_accessor import DotAccessor
from airembr.system.command.collect.errors import CollectorError
from airembr.system.command.collect.observations import collect_observations
from airembr.system.process.logging.log_handler import get_logger
from airembr.system.process.sourcing.source_validation import validate_source
from airembr_sdk.core.date import now_in_utc

logger = get_logger(__name__)


async def collect_redirect_observation(source_id: str, params: dict, headers: Headers) -> str:
    """Builds and dispatches the "traffic redirect" observation, returning the resolved
    redirect_url. A redirect must always happen once we know where to send the visitor,
    so tracking/dispatch failures are logged and swallowed here rather than raised —
    only a missing/invalid source configuration (no redirect_url to send them to at all,
    or a missing customer id) is a real error.
    """
    headers[X_BRIDGE] = 'redirect'
    in_test_mode = params.get('__dry_run', None) is not None
    headers[X_CONTEXT] = V_STAGING if in_test_mode else V_PRODUCTION

    source = await validate_source(headers, source_id, allowed_bridges=['redirect'])

    dot = DotAccessor(payload={"param": params})
    converter = DictTraverser(dot)
    event_properties = json.loads(source.config.get('event_properties', 'null'))
    event_properties_dict = converter.reshape(event_properties)

    redirect_url = source.config.get('redirect_url', None)
    event_type = source.config.get('event_type', None)
    customer_id_param = source.config.get('customer_id', None)

    if redirect_url is None or not redirect_url.strip():
        raise CollectorError(detail=f"No redirect url set. See Source id: '{source_id}'", status_code=422)

    if customer_id_param is None or not customer_id_param.strip():
        raise CollectorError(detail=f"No customer if set. See Source id: '{source_id}'", status_code=422)

    customer_id = params.get(customer_id_param, None) if customer_id_param else None

    if customer_id is None or not customer_id.strip():
        raise CollectorError(
            detail=f"No customer ID param '{customer_id_param}' in URL. See Source id: '{source_id}'.",
            status_code=422)

    customer_instance = f"person #{customer_id}"

    observation = Observation(
        name="Traffic Redirect",
        source=Entity(id=source_id),
        entities={
            "person-1": {
                "instance": customer_instance
            },
            "page-1": {
                "instance": "page #url.#",
                "traits": {
                    "url": redirect_url
                }
            }
        },
        relation=[
            ObservationRelation(
                ts=now_in_utc(),
                actor='person-1:user',
                type='event',
                label=event_type if event_type else 'redirected-to',
                objects=["page-1"],
                traits=event_properties_dict
            )
        ]
    )

    try:
        await collect_observations([observation], headers)
    except CollectorError as e:
        logger.warning(f"Redirect tracking failed for source '{source_id}', redirecting anyway: {e}")

    return redirect_url
