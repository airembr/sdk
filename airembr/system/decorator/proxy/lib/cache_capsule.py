import dataclasses
from typing import Optional, Awaitable, Callable, Any, Dict, Tuple
from pydantic import BaseModel


@dataclasses.dataclass
class FunctionCache:
    func: Callable[..., Awaitable[Any]]
    func_args: Tuple
    func_kwargs: Dict[str, Any]

    def _key(self):
        return (f"{self.func.__name__}", *self.func_args, frozenset(self.func_kwargs.items()))

    def __hash__(self):
        return hash(self._key())

    def key(self) -> str:
        return f"{self.func.__name__}.{hash(self)}"

    async def run(self):
        return await self.func(*self.func_args, **self.func_kwargs)


class CacheCapsule(BaseModel):
    name: str
    cache_ttl: Optional[int]
    max_no_exec_time: Optional[float] = 0
    callable: FunctionCache

    def __init__(self, /, **data: Any):
        super().__init__(**data)
        if self.cache_ttl and self.max_no_exec_time < self.cache_ttl:
            raise ValueError(
                f"The maximum execution time cannot be shorter than the cache duration. If the function is cached, it will not even be considered for execution.")
