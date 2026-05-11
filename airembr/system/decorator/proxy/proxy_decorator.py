import functools
from typing import Optional, List, Callable, Type, Union, Tuple

from airembr.system.decorator.proxy.lib.proxy import CacheProxy
from airembr.system.decorator.proxy.lib.throttle import Throttler

_cache_proxy = CacheProxy(namespace="cache:proxy")
_throttler = Throttler()


def cache_proxy(name: str,
                in_memory_cache_ttl: Optional[int],
                max_no_exec_time: float,
                global_cache_ttl: Optional[int] = 60*60*24,  # 1d
                cache_key_func: Optional[Callable[[tuple, dict], str]] = None,
                expect_value_type: Optional[Union[Type, Tuple[Type]]] = None,
                ):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Use the CacheProxy to execute the function
            # cache_capsule = CacheCapsule.model_construct(
            #     name=name,
            #     in_memory_cache_ttl=in_memory_cache_ttl,
            #     max_no_exec_time=max_no_exec_time,
            #     callable=FunctionCache(func=func, func_args=args, func_kwargs=kwargs)
            # )

            # callable=FunctionCache(func=func, func_args=args, func_kwargs=kwargs)

            result, status = await _cache_proxy.get(
                name,
                in_memory_cache_ttl,
                global_cache_ttl,
                max_no_exec_time,
                cache_key_func,
                # Function to call
                func,
                args,
                kwargs,
                # In Memory Cache
                _throttler)

            status.print_in_memory(result, all=False)
            status.print_global(result, all=True)

            if expect_value_type and not isinstance(result, expect_value_type):
                raise ValueError(f"Expected value type {expect_value_type} from cache {name}:{func.__name__}, got ({type(result)})")

            return result

        return wrapper

    return decorator


def invalidate_cache_proxy(names: List[str]):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Use the CacheProxy to execute the function
            return await _cache_proxy.invalidate(names, func, args, kwargs)

        return wrapper

    return decorator
