from sdk.defer_adapter import queue_type

from sdk.defer.model.adapter import Adapter
from sdk.defer.service.singleton import Singleton
from sdk.defer_adapter.adapters import collector_queue_adapter, function_queue_adapter, workflow_queue_adapter, \
    destination_queue_adapter, logger_queue_adapter, event_property_adapter, event_attachment_adapter


class DeferAdapterSelector(metaclass=Singleton):

    def __init__(self):

        #
        # ai_summary_consumer = ai_queue_adapter()
        # ai_summary_consumer.override_function = (
        #     "bg.wk.background.consumer.ai.summarizer.main",
        #     "init")
        # ai_summary_consumer.override_function = (
        #     "bg.wk.background.consumer.ai.summarizer.main",
        #     "context_enhancer_consumer")
        # ai_summary_consumer.override_batcher = (None, None, 0, 0, 0)  # Reset to no bulker


        self._adapters = {
            queue_type.FUNCTION: (function_queue_adapter, True),
            queue_type.COLLECTOR: (collector_queue_adapter, True),
            queue_type.WORKFLOW: (workflow_queue_adapter, True),
            queue_type.DESTINATION: (destination_queue_adapter, True),
            queue_type.LOGGER: (logger_queue_adapter, True),
            queue_type.PROPERTIES: (event_property_adapter, True), # False if custom consumer that attaches to existing queue without adapter
            queue_type.ATTACHMENTS: (event_attachment_adapter, True),
        }

    def get(self, adapter_name, queue_tenant: str) -> Adapter:
        if adapter_name not in self._adapters:
            raise ValueError(f"No adapter '{adapter_name}' available.")
        adapter, callable = self._adapters[adapter_name]
        if callable:
            adapter = adapter(queue_tenant)
        adapter.name = adapter_name
        return adapter
