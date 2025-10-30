from time import time
from typing import Optional, List, Any, Tuple, Callable
from pydantic import BaseModel

from sdk.defer.config import Config
from sdk.defer.error.client_timeout import PushError
from sdk.defer.model.adapter import Adapter
from sdk.defer.model.batcher import BatcherConfig
from sdk.defer.model.transport_context import TransportContext
from sdk.defer.service.error_handler import fallback_on_error
from sdk.defer.service.fallback import FallbackManager
from sdk.defer.service.invokers import invoke, async_invoke
from sdk.defer.service.logger.log_handler import get_logger, log_handler

logger = get_logger(__name__)
fallback = FallbackManager()
config = Config()

class FunctionCapsule(BaseModel):
    module: str
    name: str


class PublishPayload(BaseModel):
    capsule: 'WorkerCapsule'
    job_tag: str
    context: TransportContext
    headers: dict
    options: Optional[dict] = {}


class WorkerCapsule(BaseModel):
    function: FunctionCapsule
    args: tuple
    kwargs: dict
    guard: Optional[FunctionCapsule] = None

    def _allow(self, context: TransportContext):
        if not self.guard:
            return True
        return invoke(context, self.guard.module, self.guard.name, self.args, self.kwargs)

    async def run(self, context: TransportContext):

        if not self._allow(context):
            return None

        result = await async_invoke(context, self.function.module, self.function.name, self.args, self.kwargs)

        return result

    async def _invoke(self, batcher, context):

        # Run as asyncio task without batcher
        result = await self.run(context)

        if not batcher:
            return result, log_handler.collection

        # With batcher

        if not isinstance(result, list):
            result = [result]

        batcher_module, batcher_name = batcher.get_module_and_function()
        return await async_invoke(context, batcher_module, batcher_name, [result])

    async def push(self,
                   job_tag: str,
                   context: TransportContext,
                   batcher: Optional[BatcherConfig] = None,
                   adapter: Optional[Adapter] = None,
                   options: Optional[dict] = None,
                   on_error: Optional[Callable] = None
                   ) -> Optional[Tuple[Any, List[dict]]]:

        """
            Pushed data to pulsar topic.
        """

        if on_error is None:
            on_error_function = lambda payload: fallback_on_error(payload, adapter.name)
        else:
            on_error_function = lambda payload: on_error(payload, adapter.name)

        if options is None:
            options = {}

        assert isinstance(context, TransportContext)

        if not self._allow(context):
            return None, log_handler.collection

        if adapter is None:
            logger.warning(f"Job `{job_tag}` is running without data bus. Inline execution of the job is scheduled.")

        data_bus = adapter.adapter_protocol.data_bus()
        properties = {
            "function.name": self.function.name,
            "function.module": self.function.module,
            'data_bus.factory': type(data_bus.factory).__name__,
            # Factory models are defined in executor.py (_available_factories)
            'data_bus.schema': type(data_bus.factory.schema()).__name__,
        }

        if batcher:
            properties['batcher.module'], properties['batcher.name'] = batcher.get_module_and_function()
            properties['batcher.min_buffer'] = str(batcher.min_size)
            properties['batcher.max_buffer'] = str(batcher.max_size)
            properties['batcher.timeout'] = str(batcher.timeout)

        options['event_timestamp'] = int(time())

        try:

            if not config.queue_enabled:
                logger.debug(f"Running inline. Topic: {data_bus.topic}, job tag: {job_tag}")
                result = await self._invoke(batcher, context)
                return result, log_handler.collection

            # We had an incident with an unavailable queue
            if fallback.is_in_error_mode():
                flag = fallback.flags.get_flag(fallback.KEY)
                raise PushError(f"Running in error fallback mode. Retry in {flag.timeout()}s")

            publish_payload = PublishPayload(
                capsule=self,
                job_tag=job_tag,
                context=context,
                headers=properties,
                options=options
            )

            # Throws PushError
            result = adapter.adapter_protocol.publish(publish_payload, on_error=on_error_function)

            return result, log_handler.collection

        # On connection error
        except Exception as e:
            fallback.set_error_mode(str(e))
            logger.error(str(e))
            publish_payload = PublishPayload(
                capsule=self,
                job_tag=job_tag,
                context=context,
                headers=properties,
                options=options
            )
            if on_error_function:
                try:
                    on_error_function(publish_payload)
                except Exception as e:
                    logger.error(str(e))
            return None, log_handler.collection
