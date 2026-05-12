from airembr.model.system.context import get_context
from airembr.system.adapter.cache.cache_adaper_selector import cache_adapter

_cache = cache_adapter()

def _has_cache(key: str, key_namespace: str):
    return _cache.exists(f"{key_namespace}{key}")


def _get_key_namespace(type: str):
    context = get_context()
    return f"{type}:{context.context_abrv()}:"


def has_cache(type: str, data_hash: str) -> bool:
    key_namespace = _get_key_namespace(type)

    return _has_cache(data_hash, key_namespace)


def set_cache(type: str, key: str, ttl: int):
    key_namespace = _get_key_namespace(type)
    _cache.set(
        f"{key_namespace}{key}",
        '1',
        ex=ttl
    )


def delete_cache_node(type: str, match: str):
    key_namespace = _get_key_namespace(type)
    keys_to_delete = list(_cache.scan(f"{key_namespace}{match}"))
    if keys_to_delete:
        _cache.delete(keys_to_delete, skip_tenant=True)
