import json
import pickle

from typing import Optional, List

from pydantic import BaseModel

from airembr.system.process.logging.log_handler import get_logger
from airembr.system.process.dispatching.trigger_interface import TriggerInterface

from system.adapter.queue.pulsar.pulsar_client import PulsarClient
from airembr.model.api.request.observation import Observation

logger = get_logger(__name__)


class PulsarCredentials(BaseModel):
    host: str  # AnyHttpUrl
    token: Optional[str] = None


class PulsarTopicConfiguration(BaseModel):
    topic: str
    serializer: str = 'json'


class PulsarConnector(TriggerInterface):

    def _dispatch(self, payload, headers):
        try:
            credentials = self.resource.credentials.test if self.debug is True else self.resource.credentials.production
            credentials = PulsarCredentials(**credentials)

            init = self.destination.destination.init
            config = PulsarTopicConfiguration(**init)

            # use credentials and config to set up Apache pulsar client
            if credentials.token:
                handler = PulsarClient(
                    credentials.host,
                    credentials.token
                )
            else:
                handler = PulsarClient(
                    credentials.host
                )

            producer = None
            try:
                producer = handler.client.create_producer(config.topic,
                                                          batching_enabled=True,
                                                          batching_max_messages=1500,
                                                          batching_max_allowed_size_in_bytes=1024 * 1024,
                                                          batching_max_publish_delay_ms=100,
                                                          )

                if config.serializer == 'pickle':
                    payload = pickle.dumps(payload)

                elif config.serializer == 'json':
                    payload = json.dumps(
                        payload,
                        default=str
                    ).encode('utf-8')

                producer.send(payload, properties=headers)

            finally:
                if producer:
                    producer.close()

        except Exception as e:
            logger.error(str(e))
            raise e

    async def dispatch(self, observations: List[Observation], job_name: str = None):
        for observation in observations:
            self._dispatch(payload=observation.model_dump(mode='json'), headers={})
