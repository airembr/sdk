from typing import Optional, Dict

from pydantic import BaseModel


class TransportContext(BaseModel):
    production: bool
    tenant: str
    properties: Optional[Dict] = None

    def as_context(self) -> dict:
        return self.model_dump(mode='json', exclude={"properties": ...})

    @staticmethod
    def build(context):
        return TransportContext(tenant=context.tenant, production=context.production, properties={})
