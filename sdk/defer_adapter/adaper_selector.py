from sdk.defer.model.adapter import Adapter
from sdk.defer.service.singleton import Singleton
from sdk.defer_adapter.adapters import collector_queue_adapter, function_queue_adapter, workflow_queue_adapter, \
    destination_queue_adapter, logger_queue_adapter, event_property_queue_adapter, ai_ner_queue_adapter, \
    ai_queue_adapter


class DeferAdapterSelector(metaclass=Singleton):
    FUNCTION = 'system.function'
    COLLECTOR = 'system.collector'
    WORKFLOW = 'system.workflow'
    DESTINATION = 'system.destination'
    LOGGER = 'system.logger'
    PROPERTIES = 'system.event.properties'
    EMBEDDINGS = 'system.ai.embeddings'
    # SUMMARY = 'system.ai.summary'
    # AI_ENTITY_RECOGNITION = 'system.ai.ner'

    def __init__(self):

        # Attached consumers

        event_property_consumer = event_property_queue_adapter()
        event_property_consumer.override_function = (
            "bg.wk.background.consumer.properties.main", "event_property_consumer")
        event_property_consumer.override_batcher = (None, None, 0, 0, 0)  # Reset to no bulker

        # ---

        ai_embeddings_consumer = ai_queue_adapter()
        ai_embeddings_consumer.init_function = (
            "bg.wk.ai.embeddings.main",
            "init"
        )
        ai_embeddings_consumer.override_function = (
            "bg.wk.ai.embeddings.main",
            "ai_embeddings_consumer")
        ai_embeddings_consumer.override_batcher = (
            "bg.wk.ai.embeddings.main",
            "ai_embeddings_bulk_consumer",
            0,  # min size
            500,  # Max size
            15  # timeout
        )
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
            self.FUNCTION: (function_queue_adapter, True),
            self.COLLECTOR: (collector_queue_adapter, True),
            self.WORKFLOW: (workflow_queue_adapter, True),
            self.DESTINATION: (destination_queue_adapter, True),
            self.LOGGER: (logger_queue_adapter, True),
            self.PROPERTIES: (event_property_consumer, False),  # False if custom consumer that attaches to existing queue
            self.EMBEDDINGS: (ai_embeddings_consumer, False),
            # self.SUMMARY: (ai_summary_consumer, False),
            # self.AI_ENTITY_RECOGNITION: (ai_ner_queue_adapter, True),
        }

    def get(self, adapter_name) -> Adapter:
        if adapter_name not in self._adapters:
            raise ValueError(f"No adapter '{adapter_name}' available.")
        adapter, callable = self._adapters[adapter_name]
        if callable:
            adapter = adapter()
        adapter.name = adapter_name
        return adapter
