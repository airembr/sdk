from typing import Optional

from airembr.model.api.request.time_range import DatetimeRangePayload
from airembr.sdk.service.parser.tql.filter_condition import FilterCondition
from airembr.system.adapter.bigdata.big_data_adapter import bd_log_adapter
from airembr.system.adapter.bigdata.general.utils.mapping import log_mapping


def _apply_paging_and_filter(query: DatetimeRangePayload, page: Optional[int]):
    if page is not None:
        page_size = query.limit
        query.start = page_size * page
        query.limit = page_size

    if query.where:
        parser = FilterCondition(log_mapping())
        query.where = parser.evaluate(query.where)


async def load_logs(query: DatetimeRangePayload, page: Optional[int]):
    _apply_paging_and_filter(query, page)
    return await bd_log_adapter.search_all(query)


async def load_log_histogram(query: DatetimeRangePayload, page: Optional[int]):
    _apply_paging_and_filter(query, page)
    return await bd_log_adapter.load_log_histogram(query)
