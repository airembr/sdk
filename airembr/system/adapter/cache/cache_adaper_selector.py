from airembr.system.config.sys_config import sys_config
from airembr.protocol.cache.cache_protocol import CacheProtocol
from airembr.protocol.cache.hcache_protocol import HCacheProtocol
from airembr.protocol.cache.member_cache_protocol import MemberCacheProtocol
from airembr.protocol.cache.pubsub_protocol import PubSubProtocol
from airembr.system.decorator.run_once import run_once

_cache_adapter_var = sys_config.cache_adapter

if _cache_adapter_var == 'redis':
    from airembr.system.adapter.cache.redis.lcache import RedisListCacheAdapter
    from airembr.system.adapter.cache.redis.cache import RedisCacheAdapter
    from airembr.system.adapter.cache.redis.hcache import RedisHCacheAdapter
    from airembr.system.adapter.cache.redis.members import RedisMembersCacheAdapter
    from airembr.system.adapter.cache.redis.pubsub import RedisPubSubAdapter


@run_once
def cache_adapter() -> CacheProtocol:
    if _cache_adapter_var.lower() == 'redis':
        _rcache_adapter = RedisCacheAdapter()
    else:
        raise ValueError(f"Unknown cache adapter `{_cache_adapter_var}`")

    return _rcache_adapter


@run_once
def hcache_adapter() -> HCacheProtocol:
    if _cache_adapter_var.lower() == 'redis':
        _hcache_adapter = RedisHCacheAdapter()
    else:
        raise ValueError(f"Unknown hcache adapter `{_cache_adapter_var}`")

    return _hcache_adapter


@run_once
def mcache_adapter() -> MemberCacheProtocol:
    if _cache_adapter_var.lower() == 'redis':
        _mcache_adapter = RedisMembersCacheAdapter()
    else:
        raise ValueError(f"Unknown mcache adapter `{_cache_adapter_var}`")

    return _mcache_adapter


@run_once
def pubsub_adapter() -> PubSubProtocol:
    if _cache_adapter_var.lower() == 'redis':
        _ps_cache_adapter = RedisPubSubAdapter()
    else:
        raise ValueError(f"Unknown pubsub adapter `{_cache_adapter_var}`")

    return _ps_cache_adapter

@run_once
def list_cache_adapter(prefix: str = None) -> RedisListCacheAdapter:
    if _cache_adapter_var.lower() == 'redis':
        _rcache_adapter = RedisListCacheAdapter(prefix)
    else:
        raise ValueError(f"Unknown list cache adapter `{_cache_adapter_var}`")

    return _rcache_adapter