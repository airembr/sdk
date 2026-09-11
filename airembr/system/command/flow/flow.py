from typing import Optional

from dagor.domain.flow_graph import FlowGraph
from dagor.domain.flowdag import FlowDag, FlowRecord
from dagor.domain.flow_meta_data import FlowMetaData
from dagor.interface.workflow.entrypoint import (
    delete_workflow, debug_workflow, upsert_workflow_details, load_workflow, load_workflow_dag, save_workflow,
    rearrange_workflow, load_workflows, load_workflows_metadata,
)
from airembr.system.command.flow.errors import FlowError


def rearrange_flow(flow_dag: FlowDag) -> FlowDag:
    """
    Rearranges the send workflow nodes.
    """
    return rearrange_workflow(flow_dag)


async def upsert_workflow(flow_dag: FlowDag, rearrange_nodes: Optional[bool]):
    return await save_workflow(flow_dag, rearrange_nodes)


async def load_flow_draft(workflow_id: str) -> Optional[FlowDag]:
    """
    Loads draft version of flow with given ID (str)
    """
    return await load_workflow_dag(workflow_id)


async def get_flow_details(workflow_id: str) -> Optional[FlowRecord]:
    """
    Returns flow metadata of flow with given ID (str)
    """
    try:
        return await load_workflow(workflow_id)
    except FileNotFoundError as e:
        raise FlowError(str(e), 404)


async def upsert_flow_details(flow_metadata: FlowMetaData):
    """
    Adds new flow metadata for flow with given id (str)
    """
    return await upsert_workflow_details(flow_metadata)


async def debug_flow(flow: FlowGraph) -> dict:
    """
        Debugs flow sent in request body
    """

    result = await debug_workflow(flow)

    return {
        'logs': [],
        "debugInfo": result.debug_info.model_dump(),
        "update": None,
    }


async def delete_flow(workflow_id: str) -> dict:
    """
    Deletes flow with given id (str)
    """

    await delete_workflow(workflow_id)

    return {
        "rule": True,
        "flow": True
    }


async def list_flows_ids_and_names(type: Optional[str], limit: int):
    """
    Retrieves a list of workflow metadata including IDs and names.
    """
    return await load_workflows_metadata(type, limit=limit)


async def list_flows(type: Optional[str], query: str, limit: int):
    """
    Returns workflows according to given type, query (str) and limit (int) parameters
    """
    return await load_workflows(type, query, limit=limit)
