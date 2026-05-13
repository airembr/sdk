from typing import List, Optional

from airembr.model.destination_trigger import DestinationTrigger
from airembr.system.preconfig.setup_destination_triggers import destination_triggers


class DestinationTriggerService:

    @staticmethod
    def load_all() -> List[DestinationTrigger]:
        return destination_triggers

    @staticmethod
    def load_by_id(trigger_id: str) -> Optional[DestinationTrigger]:
        for trigger in destination_triggers:
            if trigger.id == trigger_id:
                return trigger
        return None
