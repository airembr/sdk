from typing import Set, Tuple

from pararun_adapter.pulsar.config import PulsarConfig
from pararun_adapter.pulsar.pulsar_topic_config import PulsarTopicConfig
from pararun_adapter.pulsar.client.pulsar_manager_client import PulsarManagerClient, PulsarClientError

from airembr.system.process.logging.log_handler import get_logger

logger = get_logger(__name__)


class PulsarSetup:

    def __init__(self, service_host, broker_host, token=None):
        self.broker_host = broker_host
        self.service_host = service_host
        self.client = PulsarManagerClient(service_host, token)

    async def setup_tenant(self, tenant, cluster):

        clusters = [c async for c in self.client.list_clusters()]
        if cluster not in clusters:
            raise PulsarClientError(f"Cluster '{cluster}' not configured in Pulsar. Pulsar has the following "
                                    f"clusters defined {clusters}")

        try:
            await self.client.create_tenant(tenant, [cluster])
        except PulsarClientError as e:
            logger.warning(str(e))

    async def setup_namespaces(self, tenant, namespaces: Set[Tuple[str, int, int, int]]):
        for namespace, ttl, size_in_mb, time_in_minutes in namespaces:
            try:
                await self.client.create_namespace(tenant, namespace)
                await self.client.set_namespace_ttl(tenant, namespace, ttl)
                await self.client.set_namespace_retention(tenant, namespace, size_in_mb, time_in_minutes)
                await self.client.get_namespace_ttl(tenant, namespace)
                await self.client.get_namespace_retention(tenant, namespace)
            except PulsarClientError as e:
                logger.warning(f"Namespace {tenant}/{namespace}: {str(e)}")

    async def setup_partitioned_topics(self, tenant, namespace, topics: Set[Tuple[str, int]]):
        for topic, partitions in topics:
            try:
                has_topic = await self.client.has_partitioned_topic(tenant, namespace, topic)
                if not has_topic:
                    logger.info(f"Setting partitioned topic {tenant}/{namespace}/{topic}.")
                    await self.client.create_partitioned_topic(tenant, namespace, topic, partitions)
                else:
                    logger.info(f"Partitioned topic {tenant}/{namespace}/{topic} EXISTS.")

            except PulsarClientError as e:
                logger.warning(f"Topic {tenant}/{namespace}/{topic}: {str(e)}")

    async def auto_setup(self, tenant: str):

        topic_config = PulsarTopicConfig()
        pulsar_config = PulsarConfig()

        cluster = pulsar_config.pulsar_cluster

        ttl_14_days = topic_config.system_namespace_ttl
        retention_size_mb = topic_config.system_namespace_retention_size  # 1Gi
        retention_time_in_min = topic_config.system_namespace_retention

        logger.info("Running Pulsar SetUp.")
        namespaces = {
            (topic_config.system_namespace, ttl_14_days, retention_size_mb, retention_time_in_min),
        }

        topics = {
            (topic_config.function_topic, topic_config.function_topic_partitions),  # Topic, number of partitions
            (topic_config.collector_topic, topic_config.collector_topic_partitions),
            (topic_config.workflow_topic, topic_config.workflow_topic_partitions),
            (topic_config.destination_topic, topic_config.destination_topic_partitions),
            (topic_config.log_topic, topic_config.log_topic_partitions),
            (topic_config.event_attachment_topic, topic_config.event_attachment_topic_partitions),
            (topic_config.entity_properties_merger_topic, topic_config.entity_properties_merger_topic_partitions)
        }

        await self.setup_tenant(tenant, cluster)
        await self.setup_namespaces(tenant, namespaces)
        for namespace, _, _, _ in namespaces:
            await self.setup_partitioned_topics(tenant, namespace, topics)
