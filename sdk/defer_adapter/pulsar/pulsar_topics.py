from sdk.defer_adapter.topic_config import TopicConfig


class Topics:
    
    def __init__(self):
        self.config = TopicConfig()
    
    @property
    def system_function_topic(self):
        return f"{self.config.topic_type}://{self.config.tenant}/{self.config.system_namespace}/{self.config.function_topic}"

    @property
    def collector_function_topic(self):
        return f"{self.config.topic_type}://{self.config.tenant}/{self.config.system_namespace}/{self.config.collector_topic}"

    @property
    def workflow_function_topic(self):
        return f"{self.config.topic_type}://{self.config.tenant}/{self.config.system_namespace}/{self.config.workflow_topic}"

    @property
    def destination_function_topic(self):
        return f"{self.config.topic_type}://{self.config.tenant}/{self.config.system_namespace}/{self.config.destination_topic}"

    @property
    def logger_function_topic(self):
        return f"{self.config.topic_type}://{self.config.tenant}/{self.config.system_namespace}/{self.config.log_topic}"

    @property
    def ai_ner_topic(self):
        return f"{self.config.topic_type}://{self.config.tenant}/{self.config.system_namespace}/{self.config.ai_ner_topic}"


pulsar_topics = Topics()
