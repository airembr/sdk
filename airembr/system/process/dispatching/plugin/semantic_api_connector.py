import asyncio
from collections import defaultdict

import aiohttp
from typing import Optional, List, Any, Dict, Tuple
from json import JSONDecodeError
from pydantic import BaseModel
from aiohttp import ClientConnectorError, BasicAuth, ContentTypeError

from airembr_sdk.core.entity.identification import generate_pk
from airembr.model.system.observation import Observation

from airembr.system.process.logging.log_handler import get_logger
from airembr.system.process.dispatching.trigger_interface import TriggerInterface

logger = get_logger(__name__)


class SemanticApiConfiguration(BaseModel):
    timeout: int = 30
    headers: Optional[dict] = {}
    ssl_check: bool = True
    url: str  # AnyHttpUrl
    username: Optional[str] = None
    password: Optional[str] = None
    proxy: Optional[str] = None

    def __init__(self, /, **data: Any):
        super().__init__(**data)
        self.headers = {key.lower(): value for key, value in self.headers.items()}

    def has_basic_auth(self):
        return self.username and self.password


def group_observations(
    observations: List[Observation],
) -> Dict[Tuple[str, str], List[Observation]]:
    grouped = defaultdict(list)

    for obs in observations:
        observer = obs.get_observer()
        if not observer:
            continue

        observer_pk = generate_pk(observer.instance.kind,observer.instance.id)
        key = (obs.id, observer_pk)
        grouped[key].append(obs)

    return dict(grouped)


class SemanticApiConnector(TriggerInterface):

    async def _dispatch(self, observation_id, observer_pk, observation_as_text: str):
        try:

            init = self.destination.destination.init

            resource_setup = self.resource.credentials.test if self.debug is True else self.resource.credentials.production
            config = SemanticApiConfiguration(**resource_setup)

            timeout = aiohttp.ClientTimeout(total=config.timeout)

            async with aiohttp.ClientSession(timeout=timeout) as session:

                headers = dict(config.headers)
                headers['content-type'] = 'text/plain'

                logger.debug(f"Destination request to {config.url}, headers: {headers}, method: POST")

                async with session.request(
                        method='post',
                        url=f"{config.url.rstrip('/')}/v2/entity/extraction/{observation_id}/{observer_pk}",
                        headers=headers,
                        ssl=config.ssl_check,
                        auth=BasicAuth(config.username,
                                       config.password) if config.has_basic_auth() else None,
                        data=observation_as_text
                ) as response:

                    try:
                        content = await response.json(content_type=None)

                    except JSONDecodeError:
                        content = await response.text()

                    except ContentTypeError:
                        content = await response.json(content_type='text/html')

                    print(content)

        except ClientConnectorError as e:
            logger.error(str(e), e, exc_info=True)
            raise e

        except asyncio.exceptions.TimeoutError as e:
            logger.error(str(e), e, exc_info=True)
            raise e

    async def dispatch(self, observations: List[Observation], job_name: str = None):
        for (obs_id, observer_pk), observations in group_observations(observations).items():
            for observation in observations:
                text = ["\n".join(relation.semantic_summary()) for relation in observation.relation]
                await self._dispatch(obs_id, observer_pk, observation_as_text="\n".join(text))