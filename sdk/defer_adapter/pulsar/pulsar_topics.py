from sdk.defer_adapter.topic_config import TopicConfig


class Topics:
    
    def __init__(self):
        self.config = TopicConfig()
    
    def system_function_topic(self, queue_tenant: str):
        return f"{self.config.topic_type}://{queue_tenant}/{self.config.system_namespace}/{self.config.function_topic}"

    def collector_function_topic(self,  queue_tenant: str):
        return f"{self.config.topic_type}://{queue_tenant}/{self.config.system_namespace}/{self.config.collector_topic}"

    def workflow_function_topic(self, queue_tenant: str):
        return f"{self.config.topic_type}://{queue_tenant}/{self.config.system_namespace}/{self.config.workflow_topic}"

    def destination_function_topic(self, queue_tenant: str):
        return f"{self.config.topic_type}://{queue_tenant}/{self.config.system_namespace}/{self.config.destination_topic}"

    def logger_function_topic(self, queue_tenant: str):
        return f"{self.config.topic_type}://{queue_tenant}/{self.config.system_namespace}/{self.config.log_topic}"

    def event_attachment_topic(self, queue_tenant: str):
        return f"{self.config.topic_type}://{queue_tenant}/{self.config.system_namespace}/{self.config.event_attachment_topic}"


pulsar_topics = Topics()
