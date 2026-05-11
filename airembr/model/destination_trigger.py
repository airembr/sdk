from typing import Optional

from lib.common.form import Form
from airembr.model.system.named_entity import NamedEntity


class DestinationTrigger(NamedEntity):
    description: Optional[str] = ""
    config: Optional[dict] = {}
    form: Optional[Form] = None
    manual: Optional[str] = None
    outbound: Optional[str] = 'resource'
