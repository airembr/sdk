from typing import Optional, Set

from airembr.system.config.sys_config import sys_config
from airembr.model.metadata.sys_source import EventSource
from airembr.system.adapter.metadata.mysql.interface import event_source_dao
from airembr.system.process.preconfig.setup_bridges import open_rest_source_bridge
from airembr.model.system.headers import Headers
from airembr.model.system.context import get_context
from airembr.model.system.named_entity import NamedEntity
from airembr.core.time.timed_flag import suppress_for
from airembr.core.exception.exception import BlockedException
from airembr.system.process.logging.log_handler import get_logger

logger = get_logger(__name__)

async def _check_source_id(allowed_bridges, source_id) -> Optional[EventSource]:
    if not sys_config.enable_event_source_check:
        return EventSource(
            id=source_id,
            type=['rest'],
            bridge=NamedEntity(id=open_rest_source_bridge.id, name=open_rest_source_bridge.name),
            name="Static event source",
            description="This event source is prepared because of ENABLE_EVENT_SOURCE_CHECK==no.",
            channel="Web",
            transitional=False  # ephemeral
        )

    source: Optional[EventSource] = await event_source_dao.load_event_source_via_cache(source_id)

    if source is not None:

        if not source.enabled:
            raise BlockedException("Event source disabled.")

        if not source.is_allowed(allowed_bridges):
            raise BlockedException(f"This request send data of "
                                   f"type {allowed_bridges}, but the even source "
                                   f"`{source.name}`.`{source_id}` has types `{source.type}`. "
                                   f"Change bridge type in event source `{source.name}` to one that has endpoint type "
                                   f"{allowed_bridges} or call any `{source.type}` endpoint.")

    return source


async def validate_source(headers: Headers, source_id: str, allowed_bridges) -> EventSource:
    source = await _check_source_id(allowed_bridges, source_id)

    if source is None:
        context = get_context()
        raise BlockedException(f"Invalid event source `{source_id}` for tenant in `{context}`. "
                               f"Tenant or event source may not exit or data is still cached. ")

    if source.has_restricted_domain():
        origin = headers.get_origin_or_referer()

        if not origin:
            raise BlockedException(f"Event source `{source_id}` requires origin header.")

        if not source.is_allowed_domain_origin(origin):
            raise BlockedException(f"Event source `{source_id}`. Disallows url: {origin.geturl()}")

    return source

async def valid_sources(headers: Headers, source_ids: Set[str], allowed_bridges):

    for source_id in source_ids:
        try:
            await validate_source(headers, source_id, allowed_bridges)
            yield source_id
        except BlockedException as e:
            with suppress_for(f'suppress-invalid-source-{source_id}-warning', ttl=3) as suppressed:
                if not suppressed:
                    logger.warning(str(e))

