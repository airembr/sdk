import json
from hashlib import sha1
from typing import Optional

from airembr.core.singleton import Singleton
from airembr.model.metadata.sys_user import User
from airembr.protocol.cache.cache_protocol import CacheProtocol
from airembr.system.adapter.cache.cache_adaper_selector import cache_adapter
from airembr.system.command.auth.collections import Collection
from airembr.system.config.sys_config import sys_config


class TokenMemory(metaclass=Singleton):

    def __init__(self):
        self._cache: CacheProtocol = cache_adapter()
        self.ttl = 30 * 60
        instance_hash = sha1(f"{sys_config.version.version}.{sys_config.version.name}".encode("utf-8")).hexdigest()
        self.instance_hash = f"{Collection.token}{instance_hash}"

    def __setitem__(self, token, value):
        self._cache.set(f"{self.instance_hash}-{token}", value, ex=self.ttl)

    def __getitem__(self, token):
        return self._cache.get(f"{self.instance_hash}-{token}")

    def __delitem__(self, token):
        self._cache.delete(f"{self.instance_hash}-{token}")

    def refresh(self, token):
        self._cache.expire(f"{self.instance_hash}-{token}", self.ttl)


class TokenDb:

    def __init__(self):
        self._token_memory = TokenMemory()
        self.salt = "fe-skd~jS(ADsd-9328r&aS5ZFGdaF-STREas4TA"

    def _get_token(self, user: User) -> str:
        return sha1((sys_config.installation_token + user.id + self.salt).encode('utf-8')).hexdigest()

    def delete(self, token: str):
        del self._token_memory[token]

    def get(self, token: str) -> Optional[User]:
        user = self._token_memory[token]
        if user:
            user = json.loads(user)
            user = User(**user)
            return user

        return None

    def set(self, user: User) -> str:
        token = self._get_token(user)
        self._token_memory[token] = user.model_dump_json()
        return token

    def refresh(self, user: User) -> str:
        token = self._get_token(user)
        self._token_memory.refresh(token)
        return token


token2user = TokenDb()
