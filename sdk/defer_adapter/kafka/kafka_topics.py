from sdk.defer_adapter.topic_config import TopicConfig


class Topics:

    def __init__(self):
        self.config = TopicConfig()

    def system_function_topic(self, queue_tenant: str):
        return f"{queue_tenant}-{self.config.system_namespace}-{self.config.function_topic}"

    def collector_function_topic(self, queue_tenant: str):
        return f"{queue_tenant}-{self.config.system_namespace}-{self.config.collector_topic}"

    def workflow_function_topic(self, queue_tenant: str):
        return f"{queue_tenant}-{self.config.system_namespace}-{self.config.workflow_topic}"


kafka_topics = Topics()