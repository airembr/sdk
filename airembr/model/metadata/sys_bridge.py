from hashlib import md5
from typing import Optional

from airembr.model.system.named_entity import NamedEntity
from airembr.model.gui.form import Form
from airembr.core.hash.hasher import uuid4_from_md5


class Bridge(NamedEntity):
    description: Optional[str] = ""
    type: str
    config: Optional[dict] = {}
    form: Optional[Form] = None
    manual: Optional[str] = None

    def get_id_in_context_of_tenant(self, context) -> str:
        id_in_context_of_tenant = md5(f"{self.type}-{self.name}-{context.tenant}".encode()).hexdigest()
        return uuid4_from_md5(id_in_context_of_tenant)
