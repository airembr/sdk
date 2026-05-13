from typing import List, AsyncGenerator

from airembr.system.process.logging import extra_info
from airembr.system.process.logging.log_handler import get_logger

from airembr.system.process.dispatching.model.destination_payload import DestinationPayload
from airembr.model.metadata.sys_destination import Destination, DestinationConfig
from airembr.sdk.service.parser.tql.condition import Condition
from airembr.system.process.preconfig.setup_resources import get_resource_types
from airembr.system.adapter.metadata.mysql.interface import resource_dao, workflow_dao
from airembr.model.metadata.sys_resource import Resource, ResourceCredentials

logger = get_logger(__name__)


async def _check_condition(query: str, dot) -> bool:
    if query:
        condition = Condition()
        return await condition.evaluate(query, dot)
    # Return always true is not condition
    return True


async def get_destination_resource(destinations: List[Destination]) -> AsyncGenerator[
    DestinationPayload, None]:
    if not destinations:
        return

    for destination in destinations:

        # Just a precaution, destination are already filtered
        if not destination.enabled:
            continue

        if destination.is_workflow_resource():
            workflow = await workflow_dao.load_workflow(destination.resource.id)
            if not workflow or not workflow.enabled:
                logger.dev_info(f"Destination `{destination.name}` not triggered. Reason: workflow {workflow.name}(id={workflow.id}) is disabled or not found.",
                               exc_info=extra_info.exact('resource-loading',
                                                         error_number="E-0013",
                                                         package=__name__))
                continue


            # Only enabled workflows can be triggered
            resource = Resource(
                id=workflow.id,
                name=workflow.name,
                type="workflow",
                credentials = ResourceCredentials(),
                icon = 'flow',
                destination = DestinationConfig(
                    package=destination.destination.package,
                    init={
                        "dag": workflow.draft
                    },
                    form=destination.destination.form,
                    outbound=destination.destination.outbound,
                ),
                enabled = True,
                locked = workflow.lock
            )

            yield DestinationPayload(
                destination=destination,
                resource=resource
            )
        else:
            # Load resource from cache
            try:
                resource = await resource_dao.load_resource_via_cache(destination.resource.id)
                if not resource:
                    logger.dev_info(f"Destination `{destination.name}`(id:{destination.id}) not triggered. Reason: "
                                   f"Can't connect to disabled or not available Resource(id:{destination.resource.id}).")
                    continue

                yield DestinationPayload(destination=destination, resource=resource)

            except Exception as e:
                logger.error(f"Destination `{destination.name}` not triggered. Reason: {str(e)}",
                               exc_info=extra_info.exact('resource-loading',
                                                        error_number="E-0012",
                                                        package=__name__))
                continue


def get_destination_types():
    resource_types = get_resource_types()
    for resource_type in resource_types:
        if resource_type.destination is not None:
            yield resource_type.destination.package, resource_type.dict()
