from typing import Optional, Type, List, TypeVar
from durable_dot_dict.dotdict import DotDict
from srd.domain.select import Select

T = TypeVar("T", bound=DotDict)


async def load(driver,
               mapping,
               where,
               limit: Optional[int] = None,
               offset: Optional[int] = None,
               params=None,
               cast_to: Optional[Type[T]] = DotDict) -> List[T]:
    sql = Select(mapping.table).where(where).limit(limit, offset)

    records = await driver.query(sql, params)

    result = (records >> mapping).list(cast_to=cast_to)

    if not result:
        return []

    return result
