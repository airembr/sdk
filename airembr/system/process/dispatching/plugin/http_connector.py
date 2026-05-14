import asyncio
import json
import aiohttp
from datetime import datetime
from enum import Enum
from json import JSONDecodeError
from pydantic import BaseModel
from aiohttp import ClientConnectorError, BasicAuth, ContentTypeError

from typing import Optional, List

from airembr.model.api.request.observation import Observation
from airembr.sdk.service.parser.tql.utils.dictonary import flatten

from airembr.system.process.logging.log_handler import get_logger
from airembr.system.process.dispatching.trigger_interface import TriggerInterface

logger = get_logger(__name__)


class Method(str, Enum):
    post = "post"
    get = "get"
    put = "put"
    delete = 'delete'


class HttpCredentials(BaseModel):
    url: str  # AnyHttpUrl
    method: Optional[str] = 'post'
    headers: Optional[dict] = {}
    username: Optional[str] = None
    password: Optional[str] = None
    proxy: Optional[str] = None

    def has_basic_auth(self):
        return self.username and self.password


class HttpConfiguration(BaseModel):
    timeout: int = 30
    method: Optional[str] = 'post'
    headers: Optional[dict] = {}
    cookies: Optional[dict] = {}
    ssl_check: bool = True

    @staticmethod
    def _convert_params(param):
        if isinstance(param, bool):
            return 1 if param else 0
        elif isinstance(param, datetime):
            return str(datetime)
        return param

    def get_params(self, body: dict) -> dict:

        self.headers = {key.lower(): value for key, value in self.headers.items()}

        content_type = self.headers['content-type'] if 'content-type' in self.headers else 'application/json'

        if content_type == 'application/json':

            if self.method.lower() == 'get':
                params = flatten(dict(body))
                params = {key: self._convert_params(value) for key, value in params.items() if value is not None}
                return {
                    "params": params
                }

            return {
                "json": json.loads(json.dumps(body, default=str))
            }
        else:
            return {"data": json.dumps(body, default=str)}


class HttpConnector(TriggerInterface):

    @staticmethod
    def _validate_key_value(values, label):
        for name, value in values.items():
            if not isinstance(value, str):
                raise ValueError(
                    "{} values must be strings, `{}` given for {} `{}`".format(label, type(value), label.lower(),
                                                                               name))

    async def _dispatch(self, type: str, data):
        try:
            resource_setup = self.resource.credentials.test if self.debug is True else self.resource.credentials.production
            resource_setup = HttpCredentials(**resource_setup)
            self._validate_key_value(resource_setup.headers, "Header")

            init = self.destination.destination.init

            config = HttpConfiguration(**init)
            config.method = resource_setup.method
            config.headers = resource_setup.headers

            self._validate_key_value(config.cookies, "Cookie")

            timeout = aiohttp.ClientTimeout(total=config.timeout)
            url = str(resource_setup.url)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                params = config.get_params(data)

                headers = dict(config.headers)
                headers['x-dispatch-type'] = type

                logger.debug(f"Destination request to {url}, headers: {headers}, method: {config.method}")

                async with session.request(
                        method=config.method,
                        url=url,
                        headers=headers,
                        cookies=config.cookies,
                        ssl=config.ssl_check,
                        auth=BasicAuth(resource_setup.username,
                                       resource_setup.password) if resource_setup.has_basic_auth() else None,
                        **params
                ) as response:

                    try:
                        content = await response.json(content_type=None)

                    except JSONDecodeError:
                        content = await response.text()

                    except ContentTypeError:
                        content = await response.json(content_type='text/html')

                    # result = {
                    #     "status": response.status,
                    #     "content": content
                    # }

                    logger.debug(f"Destination response from {url}, status: {response.status}, content: {content}")

                    # todo log

        except ClientConnectorError as e:
            logger.error(str(e), e, exc_info=True)
            raise e

        except asyncio.exceptions.TimeoutError as e:
            logger.error(str(e), e, exc_info=True)
            raise e

    async def dispatch(self,  observations: List[Observation], job_name: str = None):
        for observation in observations:
            await self._dispatch("event", observation.model_dump(mode="json"))
