from pydantic import BaseModel
from typing import Optional, List
from hashlib import md5
import os

from airembr.sdk.service.environment import get_env_as_bool

APP_NAME = 'airembr'
VERSION = os.environ.get('_DEBUG_VERSION', '0.0.1')
TENANT_NAME = os.environ.get('TENANT_NAME', None)
PRODUCTION = os.environ.get('PRODUCTION', 'no').lower() == 'yes'
MULTI_TENANT = get_env_as_bool('MULTI_TENANT', "no")


class Version(BaseModel):
    version: str
    name: Optional[str] = None
    upgrades: List[str] = []
    production: bool = False
    config: Optional[dict] = {}
    db_version: str = '200'
    mysql_version: int = 1
    multi_tenant: Optional[bool] = False

    def __init__(self, **data):
        super().__init__(**data)
        if not self.name:
            self.name = Version._generate_name(self.db_version)

    @staticmethod
    def _generate_name(version):
        """
        e.g. ask8d7
        """
        return md5(version.encode('utf-8')).hexdigest()[:5]

    @staticmethod
    def generate_prefix(version):
        return version.replace(".", "")

    def get_version_prefix(self):
        """
        e.g. 070
        """
        version_prefix = Version.generate_prefix(self.db_version)
        return version_prefix

    def __eq__(self, other: 'Version') -> bool:
        return other and self.version == other.version and self.name == other.name

    def __str__(self):
        return f"Version {self.version}.{self.name} (DB: {self.db_version})"

    def add_upgrade(self, name: str) -> None:
        upgrades = set(self.upgrades)
        upgrades.add(name)
        self.upgrades = list(upgrades)


version: Version = Version(version=VERSION, name=TENANT_NAME, production=PRODUCTION, multi_tenant=MULTI_TENANT)
