from srd.domain.select import Select
from airembr.system.adapter.bigdata.starrocks.starrocks_base_adapter import StarrocksBaseAdapter
from typing import List, Tuple, Callable, Dict, Any, Optional
from datetime import datetime
from srd.domain.column import Column
from srd.domain.result import Result


async def aggregate(driver: StarrocksBaseAdapter,
                    mapping,
                    agg_col: Column,
                    group_by_col: Column,
                    order_by_col: Optional[List[Tuple[Column, str]]] = None,
                    where: Optional[str] = None,
                    limit: Optional[int] = None,
                    offset: Optional[int] = None,
                    params=None) -> Result:
    sql = (
        Select(mapping.table).
        columns([group_by_col, agg_col]).
        where(where).
        group([group_by_col]).
        order(order_by_col).
        limit(limit, offset)
    )

    return await driver.query(sql, params)


def bucket_data(
        data: List[Tuple[float, int]],  # list of (timestamp, count)
        start: datetime,
        end: datetime,
        num_buckets: int,
        key_formatter: Callable[[float, float, float], Any] = lambda lo, hi, interval: f"{lo:.0f}-{hi:.0f}"
) -> Dict[Any, int]:
    """
    Buckets the input data into a specified number of intervals.

    :param data: List of tuples where each tuple is (timestamp, count)
    :param start: Start datetime of the range
    :param end: End datetime of the range
    :param num_buckets: Number of buckets to create
    :param key_formatter: Function to create a key for each bucket given (bucket_start, bucket_end, interval)
    :return: A dictionary mapping bucket keys to summed counts
    """
    start_ts, end_ts = start.timestamp(), end.timestamp()
    total_span = end_ts - start_ts
    interval = total_span / num_buckets

    # Initialize buckets with a key for each bucket and a count of 0.
    buckets: Dict[Any, int] = {}
    for i in range(num_buckets):
        bucket_lo = start_ts + i * interval
        bucket_hi = bucket_lo + interval
        key = key_formatter(bucket_lo, bucket_hi, interval)
        buckets[key] = 0

    # Bucket the results: assume each data item belongs to one bucket
    for ts, count in data:
        # Find the bucket index for the current timestamp.
        # Clamp the index in case the timestamp equals the end of the interval.
        bucket_index = int((ts - start_ts) / interval)
        if bucket_index >= num_buckets:
            bucket_index = num_buckets - 1

        bucket_lo = start_ts + bucket_index * interval
        bucket_hi = bucket_lo + interval
        key = key_formatter(bucket_lo, bucket_hi, interval)
        if key not in buckets:
            buckets[key] = 0
        buckets[key] += count

    return buckets
