from typing import List

from airembr.system.process.logging.log_handler import get_logger
from airembr.system.process.dispatching.trigger_interface import TriggerInterface
from airembr.model.api.request.observation import Observation
from airembr.system.utils.text.formaters import format_observation

logger = get_logger(__name__)


class FactPrinterConnector(TriggerInterface):

    async def dispatch(self, observations: List[Observation], job_name: str = None):
        for observation in observations:
            print(format_observation(observation))
