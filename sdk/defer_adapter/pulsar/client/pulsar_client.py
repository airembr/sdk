import logging
from uuid import uuid4

import pulsar

from time import sleep
from typing import Optional, Callable

from pulsar import TopicNotFound
from pulsar.schema import BytesSchema

from sdk.defer.model.worker_capsule import PublishPayload
from sdk.defer.service.logger.log_handler import get_logger
from sdk.defer.service.singleton import Singleton

pulsar_logger = logging.getLogger('pulsar')
pulsar_logger.setLevel(logging.WARNING)

logger = get_logger(__name__)


def send_async_message(producer, message, payload: PublishPayload, on_error: Callable):
    if payload.options is None:
        options = {}
    else:
        options = payload.options

    def _callback(res, payload):
        if res != pulsar.Result.Ok:
            logger.warning("Queue could not be reached. Fallback function executed.")
            on_error(payload)
        else:
            logger.info(f"Pushed to topic: {producer.topic()}, job tag: {payload.job_tag}")

    return producer.send_async(message, lambda res, _: _callback(res, payload), properties=payload.headers,
                               **options)


# def send_async_message(producer, message, properties, retries, options: Optional[dict],
#                        on_error: Callable = None):
#     if options is None:
#         options = {}
#
#     def _callback(res, message):
#         raise Exception('xxx')
#         nonlocal retries
#         try:
#             if res != pulsar.Result.Ok:
#
#                 if retries <= 0:
#                     raise ConnectionError(f"Could not connect to pulsar.")
#
#                 retries -= 1
#                 logger.warning(f"Send failed, retrying... {retries} retries left.")
#                 return producer.send_async(message, _callback, properties=properties, **options)
#
#         except Exception as e:
#             if on_error:
#                 on_error(f"Could not connect to pulsar. Detail: {str(e)}")
#
#     return producer.send_async(message, lambda res, _: _callback(res, message), properties=properties, **options)


class PulsarClient(metaclass=Singleton):

    def __init__(self, host: str, token: Optional[str] = None):

        self.host = host

        if token:
            logger.info(f"Connecting to pulsar host {host} with token.")
            self.client = pulsar.Client(
                host,
                authentication=pulsar.AuthenticationToken(token),
                connection_timeout_ms=1000,
                logger=pulsar_logger
            )
        else:
            logger.info(f"Connecting to pulsar host {host}.")
            self.client = pulsar.Client(
                host,
                connection_timeout_ms=1000,
                logger=pulsar_logger
            )

    def close(self):
        self.client.close()


class PulsarTopic:

    def __init__(self, pulsar: PulsarClient, topic: str):
        self.pulsar = pulsar
        self.topic = topic
        self.max_send_attempts = 1
        self.max_receive_attempts = 5
        self.max_send_timeout = 1000

    @staticmethod
    def _get_default_schema_if_missing(kwargs):
        schema = kwargs.get('schema', None)
        if schema is None:
            schema = BytesSchema()
        return schema

    def producer(self, **kwargs) -> pulsar.Producer:

        # Example of key_shared producer
        # add as parameter: message_routing_mode=MessageRoutingMode.SinglePartition

        attempt = 0

        if 'send_timeout_millis' not in kwargs:
            kwargs['send_timeout_millis'] = self.max_send_timeout

        # Set default schema if missing
        kwargs['schema'] = self._get_default_schema_if_missing(kwargs)

        while self.max_send_attempts > 0:
            attempt += 1
            self.max_send_attempts -= 1
            try:
                return self.pulsar.client.create_producer(
                    self.topic,
                    producer_name=f"System Functions - {str(uuid4())}",
                    batching_enabled=True,
                    batching_max_messages=1500,
                    batching_max_allowed_size_in_bytes=1024 * 1024,
                    batching_max_publish_delay_ms=200,
                    **kwargs)
            except TopicNotFound as e:
                logger.error(f"Attempt {attempt}. Could nto found topic {self.topic}: {e}")
                sleep(10)
            except Exception as e:
                logger.error(f"Attempt {attempt}. Pulsar producer failed with: {e}")
                sleep(10)

        raise ConnectionError(f"Could not connect to Pulsar at {self.pulsar.host}")

    def subscribe(self, **kwargs) -> pulsar.Consumer:

        attempt = 0
        # Set default schema if missing
        kwargs['schema'] = self._get_default_schema_if_missing(kwargs)

        while self.max_receive_attempts > 0:
            attempt += 1
            self.max_receive_attempts -= 1
            try:
                return self.pulsar.client.subscribe(self.topic, **kwargs)
            except Exception as e:
                logger.error(f"Attempt {attempt}. Pulsar subscription for topic {self.topic} failed with: {e}")
                sleep(10)

        raise ConnectionError("Could not connect to Pulsar")
