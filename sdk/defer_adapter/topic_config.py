import os

from sdk.defer.service.singleton import Singleton

class TopicConfig(metaclass=Singleton):
    def __init__(self):
        env = os.environ
        self.topic_type = env.get('PULSAR_TOPIC_TYPE', 'persistent')

        self.system_namespace = env.get('PULSAR_SYSTEM_NAMESPACE', 'system')
        self.function_topic = env.get('PULSAR_FUNCTION_TOPIC', 'functions')
        self.collector_topic = env.get('PULSAR_COLLECTOR_TOPIC', 'collectors')
        self.workflow_topic = env.get('PULSAR_WORKFLOW_TOPIC', 'workflows')
        self.destination_topic = env.get('PULSAR_DESTINATION_TOPIC', 'destinations')
        self.log_topic = env.get('PULSAR_LOG_TOPIC', 'logs')
        self.event_attachment_topic = env.get('PULSAR_EVENT_ATTACHMENT_TOPIC', 'event-attachments')

