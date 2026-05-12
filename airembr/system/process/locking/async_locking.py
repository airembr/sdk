import asyncio
from collections import defaultdict
from contextlib import asynccontextmanager

locks = defaultdict(asyncio.Lock)


@asynccontextmanager
async def async_lock(key: str):
    # Acquire the lock for the specific key
    async with locks[key]:
        yield
