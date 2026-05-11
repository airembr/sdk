from random import uniform
from airembr.sdk.service.environment import get_env_as_int


def _get_random_value(value) -> float:
    _span = 0.50
    lower_limit = max(value - (value * _span), value) if value < 5 else value - (value * _span)
    upper_limit = value + (value * _span)
    return int(uniform(lower_limit, upper_limit))


class MemoryCacheConfig:
    def __init__(self):
        self.default_ttl = 60  # Check every 60 sec

        self.timeout_sql_query_in = 1
        self.max_one_cache_fill_every = .5
        self.event_to_profile_coping_ttl = _get_random_value(
            get_env_as_int('EVENT_TO_PROFILE_COPY_CACHE_TTL', self.default_ttl))
        self.source_ttl = _get_random_value(get_env_as_int('SOURCE_CACHE_TTL', self.default_ttl))
        self.event_validation_cache_ttl = _get_random_value(
            get_env_as_int('EVENT_VALIDATION_CACHE_TTL', self.default_ttl))
        self.data_compliance_cache_ttl = _get_random_value(
            get_env_as_int('DATA_COMPLIANCE_CACHE_TTL', self.default_ttl))
        self.event_mapping_cache_ttl = _get_random_value(get_env_as_int('EVENT_METADATA_CACHE_TTL', self.default_ttl))
        self.trigger_rule_cache_ttl = _get_random_value(get_env_as_int('TRIGGER_RULE_CACHE_TTL', self.default_ttl))
        self.destination_cache_ttl = _get_random_value(get_env_as_int('DESTINATION_CACHE_TTL', 180))
        self.event_reshaping_cache_ttl = _get_random_value(
            get_env_as_int('EVENT_RESHAPING_CACHE_TTL', self.default_ttl))
        self.identification_points_cache_ttl = _get_random_value(
            get_env_as_int('IDENTIFICATION_POINTS_CACHE_TTL', self.default_ttl))
        self.resource_load_cache_ttl = _get_random_value(get_env_as_int('RESOURCE_LOAD_CACHE_TTL', self.default_ttl))


memory_cache_config = MemoryCacheConfig()
