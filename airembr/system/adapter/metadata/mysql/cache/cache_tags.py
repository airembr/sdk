from airembr.system.config.memory_cache_config import memory_cache_config
from airembr.system.adapter.metadata.mysql.schema.table import DestinationTable, \
    ResourceTable, EventValidationTable, EventMappingTable, \
    EventReshapingTable, EventSourceTable

_global_cache_ttl=60*60 # 1h

EVENT_SOURCE_TAG = dict(
    name=EventSourceTable.__tablename__,
    in_memory_cache_ttl=memory_cache_config.source_ttl,
    max_no_exec_time=memory_cache_config.source_ttl + 30,
    global_cache_ttl=_global_cache_ttl
)
EVENT_RESHAPING_TAG = dict(
    name=EventReshapingTable.__tablename__,
    in_memory_cache_ttl=memory_cache_config.event_reshaping_cache_ttl,
    max_no_exec_time=memory_cache_config.event_reshaping_cache_ttl + 30,
    global_cache_ttl=_global_cache_ttl
)
EVENT_MAPPING_TAG = dict(
    name=EventMappingTable.__tablename__,
    in_memory_cache_ttl=memory_cache_config.event_mapping_cache_ttl,
    max_no_exec_time=memory_cache_config.event_mapping_cache_ttl + 30,
    global_cache_ttl=_global_cache_ttl
)
EVENT_VALIDATION_TAG = dict(
    name=EventValidationTable.__tablename__,
    in_memory_cache_ttl=memory_cache_config.event_validation_cache_ttl,
    max_no_exec_time=memory_cache_config.event_validation_cache_ttl + 30,
    global_cache_ttl=_global_cache_ttl
)
DESTINATION_TAG = dict(
    name=DestinationTable.__tablename__,
    in_memory_cache_ttl=memory_cache_config.destination_cache_ttl,
    max_no_exec_time=memory_cache_config.destination_cache_ttl + 30,
    global_cache_ttl=_global_cache_ttl
)
RESOURCE_TAG = dict(
    name=ResourceTable.__tablename__,
    in_memory_cache_ttl=memory_cache_config.resource_load_cache_ttl,
    max_no_exec_time=memory_cache_config.resource_load_cache_ttl + 30,
    global_cache_ttl=_global_cache_ttl
)
GEO_LOCATION_TAG = dict(
    name='geo_location',
    in_memory_cache_ttl=60,
    max_no_exec_time=90,
    global_cache_ttl=_global_cache_ttl
)
