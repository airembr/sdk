from confluent_kafka.admin import NewTopic
from airembr.system.process.logging.log_handler import get_logger
from pararun_adapter.kafka.client.kafka_admin_client import KafkaAdminClient
from pararun_adapter.kafka.kafka_topic_config import KafkaTopicConfig
from pararun_adapter.kafka.config import kafka_settings
from pararun_adapter.kafka.kafka_topics import kafka_topics
from airembr.system.config.sys_config import sys_config

logger = get_logger(__name__)


class KafkaSetup:

    def auto_setup(self):
        topic_config = KafkaTopicConfig()

        logger.info("Running Kafka SetUp.")

        topics = [
            NewTopic(
                topic=kafka_topics.function_topic(sys_config.queue_tenant),
                num_partitions=topic_config.function_topic_partitions,
                replication_factor=topic_config.function_topic_replication,
                config={
                    "retention.ms": str(topic_config.function_topic_retention_ms),
                    "cleanup.policy": "delete"
                }
            ),
            NewTopic(
                topic=kafka_topics.storage_topic(sys_config.queue_tenant),
                num_partitions=topic_config.storage_topic_partitions,
                replication_factor=topic_config.storage_topic_replication,
                config={
                    "retention.ms": str(topic_config.storage_topic_retention_ms),
                    "cleanup.policy": "delete"
                }
            ),
            NewTopic(
                topic=kafka_topics.observation_topic(sys_config.queue_tenant),
                num_partitions=topic_config.observation_topic_partitions,
                replication_factor=topic_config.observation_topic_replication,
                config={
                    "retention.ms": str(topic_config.observation_topic_retention_ms),
                    "cleanup.policy": "delete"
                }
            ),
            NewTopic(
                topic=kafka_topics.collector_topic(sys_config.queue_tenant),
                num_partitions=topic_config.collector_topic_partitions,
                replication_factor=topic_config.collector_topic_replication,
                config={
                    "retention.ms": str(topic_config.collector_topic_retention_ms),
                    "cleanup.policy": "delete"
                }
            ),
            NewTopic(
                topic=kafka_topics.workflow_topic(sys_config.queue_tenant),
                num_partitions=topic_config.workflow_topic_partitions,
                replication_factor=topic_config.workflow_topic_replication,
                config={"retention.ms": str(topic_config.workflow_topic_retention_ms)}
            ),
            NewTopic(
                topic=kafka_topics.destination_topic(sys_config.queue_tenant),
                num_partitions=topic_config.destination_topic_partitions,
                replication_factor=topic_config.destination_topic_replication,
                config={"retention.ms": str(topic_config.destination_topic_retention_ms)}
            ),
            NewTopic(
                topic=kafka_topics.logger_topic(sys_config.queue_tenant),
                num_partitions=topic_config.log_topic_partitions,
                replication_factor=topic_config.log_topic_replication,
                config={"retention.ms": str(topic_config.log_topic_retention_ms)}
            ),
            NewTopic(
                topic=kafka_topics.event_attachment_topic(sys_config.queue_tenant),
                num_partitions=topic_config.event_attachment_topic_partitions,
                replication_factor=topic_config.event_attachment_topic_replication,
                config={"retention.ms": str(topic_config.event_attachment_topic_retention_ms)}
            ),
            NewTopic(
                topic=kafka_topics.entity_properties_merger_topic(sys_config.queue_tenant),
                num_partitions=topic_config.entity_properties_merger_topic_partitions,
                replication_factor=topic_config.entity_properties_merger_topic_replication,
                config={"retention.ms": str(topic_config.entity_properties_merger_topic_retention_ms)}
            ),
        ]

        admin = KafkaAdminClient(config=kafka_settings)
        existing_topics = admin.list_topics()

        to_be_created = []
        for topic in topics:
            if topic.topic in existing_topics.topics:
                logger.info(f"Topic {topic.topic} exists")
            else:
                to_be_created.append(topic)

        if to_be_created:
            admin.create_topics(to_be_created)
