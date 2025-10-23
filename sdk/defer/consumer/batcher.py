from collections import defaultdict

from typing import Tuple, Any, Optional, List, Generator, AsyncGenerator, Dict
from contextlib import contextmanager

from pydantic import BaseModel

from sdk.defer.protocol.queue_message_protocol import MessageProtocol
from sdk.defer.service.timer import Timer


class BatchItem(BaseModel):
    data: Any
    key: Optional[tuple]
    messages: List[Any]
    reason: str


class BatchStatus(BaseModel):
    batch: List[Tuple[Any, Optional[tuple], List[Any], str]]
    needs_flushing: bool


class BatcherMetadata(BaseModel):
    min_batch_size: int
    max_batch_size: int
    max_time_without_flash: float


class Batcher:
    def __init__(self):
        self.cache = defaultdict(list)
        self.messages = defaultdict(list)
        self.flush_timer = Timer()
        self._metadata: Dict[str, BatcherMetadata] = {}

    def _has_time_passed(self, key, max_time) -> bool:
        return self.flush_timer.is_time_over(key, max_time)

    def _has_min_messages(self, key, min_size) -> bool:
        return len(self.cache[key]) >= min_size

    def _is_it_time_to_flush(self, key, min_batch_size: int, max_time_without_flash: float) -> Tuple[bool, str]:
        if min_batch_size <= 0:
            if self._has_time_passed(key, max_time=max_time_without_flash):
                return True, f'time-out-{max_time_without_flash}s'
            return False, 'accumulating'

        # Must have min messages and must be over the max_time in buffer

        if (self._has_time_passed(key, max_time=max_time_without_flash)
                and self._has_min_messages(key, min_size=min_batch_size)):
            return True, f'time-out-{max_time_without_flash}s-with-min-size-{min_batch_size}'
        return False, 'accumulating'

    def _is_full(self, key, max_batch_size):
        return len(self.cache[key]) >= max_batch_size

    def _return_state(self, key) -> List[Tuple[Any, Optional[tuple], List[MessageProtocol], str]]:
        cache = self.cache[key]
        messages = self.messages[key]

        self._reset_cache(key)

        return [(cache, key, messages, 'buffer-full')]  # Indicates a batch was processed

    def _reset_all_caches(self):
        self.cache = defaultdict(list)  # Clear cache after processing
        self.messages = defaultdict(list)

    def _reset_cache(self, key):
        self.cache[key] = []  # Clear cache after processing
        self.messages[key] = []
        del self.cache[key]
        del self.messages[key]

    def flush_all(self) -> List[Tuple[Any, Optional[tuple], List[MessageProtocol], str]]:
        cache_data = []
        if len(self.cache) > 0:

            for key, cache in self.cache.items():
                data = cache, key, self.messages[key], 'inactivity-time-out'
                cache_data.append(data)

            self._reset_all_caches()

        return cache_data

    def _flush(self, key, reason) -> List[Tuple[Any, Optional[tuple], List[MessageProtocol], str]]:
        if key in self.cache and len(self.cache) > 0:
            # First prepare data
            result = self.cache[key], key, self.messages[key], reason
            # Now clean
            self._reset_cache(key)
            return [result]
        else:
            return [[], key, [], reason]

    def _append_data(self, key, result, metadata: BatcherMetadata):

        self._metadata[key] = metadata

        if isinstance(result, (list, set)):  # Check if message is a list or a set
            if key in self.messages:
                # Existing messages under key are extended with new items
                # Convert set to list if necessary
                self.cache[key].extend(list(result))
            else:
                # Assigns new message as a list (converts set to list if message is a set)
                self.cache[key] = list(result)
        else:
            self.cache[key].append(result)

    @contextmanager
    def _get_batch_status(self, key) -> \
            Generator[BatchStatus, Any, None]:

        # Get saved metadata for given cache key
        # Each key has its own metadata (e.g. how frequently to flush)
        metadata = self._metadata[key]

        _needs_flushing, _reason = self._is_it_time_to_flush(key, metadata.min_batch_size, metadata.max_time_without_flash)

        if _needs_flushing:

            result = self._flush(key, _reason)

            yield BatchStatus(
                batch=result,
                needs_flushing=True
            )

            # Mark last flush
            self.flush_timer.reset_timer(key)

        elif self._is_full(key, metadata.max_batch_size):

            result = self._return_state(key)  # Indicates a batch was processed

            yield BatchStatus(
                batch=result,
                needs_flushing=True
            )

            # Mark last flush
            self.flush_timer.reset_timer(key)

        else:

            yield BatchStatus(
                batch=[(False, None, [], _reason)],
                needs_flushing=False
            )

    async def check_if_any_of_batches_needs_a_flush(self) -> \
    AsyncGenerator[BatchStatus, None]:

        for key in list(self.cache.keys()):
            with self._get_batch_status(key) as batch_status:
                yield batch_status

    @contextmanager
    def add(self,
            result,
            key: tuple,
            metadata: BatcherMetadata,
            message: Optional[MessageProtocol] =None) -> Generator[BatchStatus, Any, None]:

        # Append to collection
        self._append_data(key, result, metadata)

        # Add message
        if message is not None:
            self.messages[key].append(message)

        # Check if the buffer should be flushed

        _needs_flushing, _reason = self._is_it_time_to_flush(key, metadata.min_batch_size, metadata.max_time_without_flash)

        if _needs_flushing:

            result = self._flush(key, _reason)

            yield BatchStatus(
                batch=result,
                needs_flushing=True
            )

            # Mark last flush
            self.flush_timer.reset_timer(key)

            return

        elif self._is_full(key, metadata.max_batch_size):

            result = self._return_state(key)  # Indicates a batch was processed

            yield BatchStatus(
                batch=result,
                needs_flushing=True
            )

            # Mark last flush
            self.flush_timer.reset_timer(key)

            return

        yield BatchStatus(
            batch=[(False, None, [], _reason)],
            needs_flushing=False
        )

        return

    def get_stats(self, key, max_time_without_flash: float):
        _passed_time = self.flush_timer.get_passed_time(key)
        return key, _passed_time, max_time_without_flash - _passed_time
