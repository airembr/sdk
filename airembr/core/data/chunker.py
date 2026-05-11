from typing import Generator, Iterable, TypeVar

T = TypeVar("T")


def chunk_generator(
        source: Iterable[T],
        batch_size: int,
        proceed_if
) -> Generator[Generator[T, None, None], None, None]:
    it = iter(source)

    while bool(proceed_if):
        batch = []

        for _ in range(batch_size):
            if not bool(proceed_if):
                break
            try:
                item = next(it)
                batch.append(item)
            except StopIteration:
                break

        if not batch:
            break

        yield (x for x in batch)
