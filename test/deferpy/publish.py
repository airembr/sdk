import asyncio
from typing import Optional

from pydantic import BaseModel

from sdk.defer.publisher.deferer import deferred_execution
from sdk.defer_adapter import queue_type
from sdk.defer_adapter.adaper_selector import DeferAdapterSelector
from sdk.defer.model.transport_context import TransportContext


def run(context, param):
    print('run')

class Context(BaseModel):
    production: bool = False
    tenant: Optional[str] = None

async def main():
    context = Context(tenant="test")

    with deferred_execution() as defer:
        await defer(run)(1).push(
            "some-name",
            TransportContext.build(context),
            adapter=DeferAdapterSelector().get(queue_type.FUNCTION, queue_tenant='tracardi-1.1.x')
        )

asyncio.run(main())