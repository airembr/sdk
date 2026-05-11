from typing import Optional

from pydantic import BaseModel

from airembr.model.system.named_entity import NamedEntity


class Tenant(NamedEntity):
    install_token: str
    email: str
    # expire: Optional[datetime] = None


class TenantCredentials(BaseModel):
    name: str
    tms_api_key: str
    email: str
    password: str
    needs_admin: bool = True
    update_mapping: Optional[bool] = False
