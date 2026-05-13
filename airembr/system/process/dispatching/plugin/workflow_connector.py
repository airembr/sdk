from pprint import pprint
from typing import List

from airembr.model.system.observation import Observation
from dagor.domain.flow_observation import FlowObservation, Relation, Entity
from dagor.domain.flowdag import FlowDag
from dagor.interface.workflow.entrypoint import run_workflow
from dagor.utils.dag_error import DagGraphError

from airembr.system.process.logging.log_handler import get_logger
from airembr.system.preconfig.setup_destination_triggers import DT_EVENT_TRIGGER
from airembr.system.process.dispatching.trigger_interface import TriggerInterface

logger = get_logger(__name__)


class WorkflowConnector(TriggerInterface):

    async def dispatch(self, observations: List[Observation], job_name: str = None):

        if 'dag' not in self.resource.destination.init:
            logger.warning("Workflow connector is not configured properly. Missing dag config.")
            return

        print('type', self.destination.trigger.type.id)

        if self.destination.trigger.type.id == DT_EVENT_TRIGGER:
            workflow = FlowDag(**self.resource.destination.init['dag'])
            for observation in observations:
                indexed_entities = observation.get_indexed_entities()
                if observation.relation:
                    for relation in observation.relation:
                        actor = indexed_entities.get(relation.actor)
                        actor['label'] = relation.actor_label

                        _relation = Relation(**{
                            "label": relation.label,
                            "id": relation.id,
                            "type": relation.type,
                            "ts": relation.ts,
                            "traits": relation.traits if isinstance(relation.traits, dict) else {},
                            "subjective": relation.subjective,
                            "semantic": relation.text.model_dump(mode="json", exclude_none=True)
                        })

                        for object_link in relation.objects:
                            object = indexed_entities.get(object_link)
                            flow_observation = FlowObservation(
                                actor=Entity(**actor),
                                relation=_relation,
                                object=Entity(**object)
                            )

                            pprint(flow_observation)

                            try:
                                # Do not run in debug as it will remove params
                                result = await run_workflow(workflow, flow_observation, params={}, debug=False)
                                logger.debug(
                                    f"Workflow `{workflow.name}`(id: {workflow.id}) triggered successfully as destination `{self.destination.name}`(id: {self.destination.id}).")
                                for i in observations:
                                    for x in i.relation:
                                        print(x.label)
                            except DagGraphError as e:
                                logger.warning(f"Workflow `{workflow.name}` not triggered. Reason: {str(e)}")
