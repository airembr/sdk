import json
import redis
import asyncio

from json import JSONDecodeError
from pydantic import ValidationError
from typing import Any
from pydantic import BaseModel
from time import sleep
from threading import Thread

from airembr.core.singleton import Singleton
from airembr_sdk.core.date import now_in_utc
from airembr.model.metadata.sys_configuration import Configuration
from airembr.system.process.logging import extra_info
from airembr.system.process.logging.log_handler import get_logger
from airembr.system.adapter.cache.cache_adaper_selector import pubsub_adapter
from airembr.system.adapter.metadata.mysql.mapping.configuration_mapping import map_to_configuration
from airembr.system.adapter.metadata.mysql.service.configuration_service import ConfigurationService
from airembr.system.config.memory_cache_config import memory_cache_config
from airembr.system.decorator.async_cache import AsyncCache

logger = get_logger(__name__)
_pubsub_cache = pubsub_adapter()


@AsyncCache(60,
            timeout=5,
            max_one_cache_fill_every=memory_cache_config.max_one_cache_fill_every,
            return_cache_on_error=True)
async def load_global_settings_by_key(key):
    cs = ConfigurationService()
    return await cs.load_by_id(key)


class ValueMessage(BaseModel):
    key: str
    value: Any


class GlobalSettingsBroadcaster(metaclass=Singleton):

    def __init__(self):
        self.settings = GlobalSettings()
        self._channel = 'global-broadcaster'

    def _listen_for_messages(self):
        while True:
            try:
                for message in _pubsub_cache.subscribe(self._channel):
                    if message['type'] == 'message':
                        data = json.loads(message['data'])
                        data = ValueMessage(**data)
                        success = self.settings.update(key=data.key, value=data.value)
                        if success:
                            logger.info(
                                f"Received an update of global settings from other node for key `{data.key}`, value: {data.value}",
                                extra=extra_info.build('GlobalSettingsBroadcaster', object=self,
                                                      error_number="GSB-0003"))
                break
            except JSONDecodeError as e:
                logger.error(f"Could not decode message from broadcaster. details: {str(e)}",
                             extra=extra_info.build('GlobalSettingsBroadcaster', self, error_number="GSB0002"))
            except (TypeError, ValidationError):
                logger.error("Incorrect message from settings broadcaster",
                             extra=extra_info.build('GlobalSettingsBroadcaster', object=self, error_number="GSB0001"))
            except Exception:
                logger.info("Trying to reconnect to Redis...",
                            extra=extra_info.build('GlobalSettingsBroadcaster', object=self, error_number="GSB-0004"))
                sleep(5)

    def publish(self, key, value) -> bool:
        try:
            payload = ValueMessage(key=key, value=value)
            _pubsub_cache.publish(self._channel, payload.model_dump_json())
            logger.dev_info(f"Global setting for key `{key}` have been broadcast to other nodes, payload: {payload}",
                            extra=extra_info.build('GlobalSettingsBroadcaster', object=self, error_number="BSB-0006"))
            return True
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Connection lost to redis. Details: {str(e)}",
                         extra=extra_info.build('GlobalSettingsBroadcaster', object=self, error_number="GSB0005"))

            return False

    def start_background_listener(self):
        thread = Thread(target=self._listen_for_messages)
        thread.daemon = True
        thread.start()


class GlobalSettings(metaclass=Singleton):

    def __init__(self):
        self.db = {}
        self.cs = ConfigurationService()

    async def _save_in_db(self, key, value):
        configuration = Configuration(
            id=key,
            name=f"System wide env variable {key}",
            timestamp=now_in_utc(),
            config=value,
            description=f"Default value for {key}",
            enabled=True,
            tags=['settings']
        )
        logger.info(f'Global setting for key `{key}` has changed. Data have been stored in the database.',
                    extra=extra_info.build('GlobalSettings', object=self, error_number="GS-0002"))
        await self.cs.upsert(configuration)

    async def _broadcast_value(self, key, value) -> bool:
        broadcaster = GlobalSettingsBroadcaster()
        success = broadcaster.publish(key, value)

        # Wait a second and check the value
        await asyncio.sleep(1)
        new_value = await self.get(key)
        if new_value != value:
            logger.warning(f"Value may not have been broadcast or have changed within 1 sec.",
                           extra=extra_info.build('GlobalSettings', object=self, error_number="GS-0001"))

        return success

    async def _save(self, key, value):

        # Save in storage
        await self._save_in_db(key, value)

        # Propagate
        if not await self._broadcast_value(key, value):
            raise ValueError(f"Could not save global setting value.")

    async def has(self, key) -> bool:
        result = await self.get(key)
        return result is not None

    def update(self, key, value) -> bool:

        # Update only updates the value in memory and does not save it in db or broadcast to other nodes.

        if key in self.db and self.db[key] == value:
            return False
        self.db[key] = value
        return True

    async def set(self, key, value) -> bool:
        if self.update(key, value):
            await self._save(key, value)
            return True

        return False

    async def get(self, key, default=None):
        if key in self.db:
            return self.db[key]

        logger.debug(f"Global setting data {key} loaded from database",
                     extra=extra_info.build('GlobalSettings', object=self, error_number="GS-0003"))
        record = await load_global_settings_by_key(key)
        if record.exists():
            # set value and return
            configuration = record.map_to_object(map_to_configuration)
            self.db[key] = configuration.config

            return self.db[key]

        # Use default value

        if default is None:
            return None

        # Save in storage
        await self._save(key, default)

        return default
