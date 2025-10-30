import asyncio
from typing import Optional

from pydantic import BaseModel

from sdk.defer.publisher.deferer import deferred_execution, deferred_lazy_execution
from sdk.defer_adapter import queue_type
from sdk.defer_adapter.adaper_selector import DeferAdapterSelector
from sdk.defer.model.transport_context import TransportContext


class Context(BaseModel):
    production: bool = False
    tenant: Optional[str] = None

async def main():
    context = Context(tenant="test")

    with deferred_lazy_execution('test.deferpy.worker','run_function') as defer:
        await defer(1).push(
            "some-tag",
            TransportContext.build(context),
            adapter=DeferAdapterSelector().get(queue_type.FUNCTION, queue_tenant='airembr-0.0.1')
        )

asyncio.run(main())