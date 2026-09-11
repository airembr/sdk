from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Response

from airembr_api.service.grouping import get_result, get_result_as_group
from airembr_api.endpoint.gui.auth.permissions import Permissions

from dagor.domain.flow_graph import FlowGraph
from dagor.domain.flowdag import FlowDag, FlowRecord
from dagor.domain.flow_meta_data import FlowMetaData

from airembr.system.config.sys_config import sys_config
from airembr.system.command.flow.errors import FlowError
from airembr.system.command.flow.flow import (
    rearrange_flow as rearrange_flow_cmd,
    upsert_workflow as upsert_workflow_cmd,
    load_flow_draft as load_flow_draft_cmd,
    get_flow_details as get_flow_details_cmd,
    upsert_flow_details as upsert_flow_details_cmd,
    debug_flow as debug_flow_cmd,
    delete_flow as delete_flow_cmd,
    list_flows_ids_and_names as list_flows_ids_and_names_cmd,
    list_flows as list_flows_cmd,
)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.post("/v2/workflow/rearrange",
             tags=["workflow"],
             response_model=FlowDag,
             include_in_schema=sys_config.expose_gui_api)
async def rearrange_flow(flow_dag: FlowDag):
    """
    Rearranges the send workflow nodes.
    """
    return rearrange_flow_cmd(flow_dag)


@router.post("/v2/workflow/dag",
             tags=["workflow"],
             include_in_schema=sys_config.expose_gui_api)
async def upsert_workflow(flow_dag: FlowDag, rearrange_nodes: Optional[bool] = False):
    return await upsert_workflow_cmd(flow_dag, rearrange_nodes)


@router.get("/v2/workflow/dag/{workflow_id}", tags=["workflow"], response_model=Optional[FlowDag], include_in_schema=sys_config.expose_gui_api)
async def load_flow_draft(workflow_id: str, response: Response):
    """
    Loads draft version of flow with given ID (str)
    """

    flow_record = await load_flow_draft_cmd(workflow_id)

    if flow_record is None:
        response.status_code = 404
        return None

    return flow_record


@router.get("/v2/workflow/{workflow_id}",
            tags=["workflow"],
            response_model=Optional[FlowRecord],
            include_in_schema=sys_config.expose_gui_api)
async def get_flow_details(workflow_id: str):
    """
    Returns flow metadata of flow with given ID (str)
    """
    try:
        return await get_flow_details_cmd(workflow_id)
    except FlowError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.post("/v2/workflow",
             tags=["workflow"],
             include_in_schema=sys_config.expose_gui_api)
async def upsert_flow_details(flow_metadata: FlowMetaData):
    """
    Adds new flow metadata for flow with given id (str)
    """
    return await upsert_flow_details_cmd(flow_metadata)

# TODO probably not used
# @router.get("/flow/{workflow_id}/lock/{lock}", tags=["flow"],
#             include_in_schema=sys_config.expose_gui_api)
# async def update_flow_lock(workflow_id: str, lock: str):
#     """
#     Handles the request to update the lock status of a specific workflow by its ID.
#
#     Updates the lock state of a given workflow to lock or unlock based on the
#     provided parameters. This endpoint is included in the schema for GUI API
#     exposure.
#
#     Parameters:
#     workflow_id (str): The ID of the workflow to update.
#     lock (str): The new lock state to apply to the workflow.
#
#     Returns:
#     Any: The result of the workflow lock update process.
#     """
#     return await update_workflow_lock(workflow_id, lock)


@router.post("/v2/workflow/debug", tags=["workflow"],
             include_in_schema=sys_config.expose_gui_api)
async def debug_flow(flow: FlowGraph):
    """
        Debugs flow sent in request body
    """

    return await debug_flow_cmd(flow)


@router.delete("/v2/workflow/{workflow_id}", tags=["workflow"],
               response_model=dict,
               include_in_schema=sys_config.expose_gui_api)
async def delete_flow(workflow_id: str):
    """
    Deletes flow with given id (str)
    """

    return await delete_flow_cmd(workflow_id)


# Workflows
@router.get("/v2/workflows/meta", tags=["workflow"],
            include_in_schema=sys_config.expose_gui_api)
async def list_flows_ids_and_names(type: Optional[str] = None, limit: int = 500):
    """
    Retrieves a list of workflow metadata including IDs and names.

    This function fetches workflow metadata based on the provided type and
    limit arguments. It queries the backend for workflows' IDs and names,
    and wraps the resulting data in a returnable structure.

    Parameters:
    type: Optional[str]
        The type of workflows to filter by. If not specified, all types
        will be included in the results.
    limit: int
        The maximum number of workflows to retrieve. Defaults to 500.

    Returns:
    dict
        A dictionary containing the list of workflows' metadata and the
        total count.

    Raises:
    Exception
        If there is an error during data retrieval.
    """
    result, total = await list_flows_ids_and_names_cmd(type, limit)
    return get_result(list(result), total)


@router.get("/v2/workflows", tags=["workflow"], include_in_schema=sys_config.expose_gui_api,
            dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
            )
async def list_flows(type: Optional[str] = None, query: str = None, limit: int = 100):
    """
    Returns workflows grouped according to given query (str) and limit (int) parameters
    """
    result, total = await list_flows_cmd(type, query, limit)
    return get_result_as_group("Workflows", list(result), total)
