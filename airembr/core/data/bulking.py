def bulker(iterable, batch_size):
    buffer = []

    for item in iterable:
        buffer.append(item)
        if len(buffer) == batch_size:
            yield buffer
            buffer = []

    # Yield remaining items (if any)
    if buffer:
        yield buffer

async def async_bulker(async_iterable, batch_size):
    buffer = []

    async for item in async_iterable:
        buffer.append(item)
        if len(buffer) == batch_size:
            yield buffer
            buffer = []

    if buffer:
        yield buffer