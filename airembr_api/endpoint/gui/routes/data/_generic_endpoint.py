# from typing import Optional
#
# from fastapi import APIRouter
# from fastapi import Depends
#
# from airembr.system.adapter.bigdata.big_data_adapter import *
# from system.query.autocomplete import KQLAutocomplete
# from tracardi.domain.sql_query import SqlQuery
# from airembr.model.api.time_range import DatetimeRangePayload
# from airembr_api.endpoint.gui.auth.permissions import Permissions
# from airembr.system.config.sys_config import sys_config
#
# router = APIRouter(
#     dependencies=[Depends(Permissions(roles=["admin", "developer", "marketer", "maintainer"]))]
# )
#
# @router.get("/{entity_name}/query/autocomplete",
#             tags=["autocomplete"],
#             include_in_schema=sys_config.expose_gui_api)
# async def autocomplete_kql(entity_name, query: Optional[str] = ""):
#     try:
#         ac = KQLAutocomplete(index=entity_name)
#         next_values, current = await ac.autocomplete(query)
#         return {
#             "next": next_values,
#             "current": current
#         }
#     except Exception as e:
#         print(e)
#         return []
#
#
# @router.post("/{entity_name}/select/range/page/{page}",
#              tags=["data"],
#              include_in_schema=sys_config.expose_gui_api)
# @router.post("/{entity_name}/select/range",
#              tags=["data"],
#              include_in_schema=sys_config.expose_gui_api)
# async def time_range_with_sql(entity_name: str, query: DatetimeRangePayload, page: Optional[int] = None):
#     if page is not None:
#         page_size = query.limit
#         query.start = page_size * page
#         query.limit = page_size
#
#     return await bd_search_adapter.search_in_time_range(entity_name, query)
#
#
# @router.post("/{entity_name}/select",
#              tags=["data"],
#              include_in_schema=sys_config.expose_gui_api)
# async def select_by_sql(entity_name: str, query: Optional[SqlQuery] = None):
#     if query is None:
#         query = SqlQuery()
#     return await bd_search_adapter.search_with_query(entity_name, query.where, start=0, limit=query.limit)
#
#
#
#
# @router.post("/{entity_name}/select/histogram",
#              tags=["data"],
#              include_in_schema=sys_config.expose_gui_api)
# async def histogram_with_sql(entity_name: str, query: DatetimeRangePayload, group_by: str = None):
#     return await bd_search_adapter.search_histogram_in_time_range(entity_name, query, group_by)
