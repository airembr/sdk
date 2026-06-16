from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from hashlib import md5
import os

from airembr.core.env.validator import get_env_as_bool
from airembr.sdk.ai.config import embedding_host, embedding_api_key, LLM_PROVIDER_API_KEY, LLM_PROVIDER, LLM_QUERY_MODEL
from airembr.system.license.license_verifier import system_license

APP_NAME = 'airembr'
VERSION = os.environ.get('_DEBUG_VERSION', '0.0.2')
TENANT_NAME = os.environ.get('TENANT_NAME', None)
PRODUCTION = os.environ.get('PRODUCTION', 'no').lower() == 'yes'
MULTI_TENANT = get_env_as_bool('MULTI_TENANT', "no")


class Version(BaseModel):
    version: str
    name: Optional[str] = None
    production: bool = False
    config: Dict[str, Any] = {}
    db_version: str = '002'
    mysql_version: int = 1
    multi_tenant: Optional[bool] = False
    feature: Dict[str, bool] = {}

    def __init__(self, **data):
        super().__init__(**data)
        if not self.name:
            self.name = Version._generate_name(self.db_version)

        if LLM_PROVIDER_API_KEY:
            self.config['llm_provider'] = LLM_PROVIDER
            self.config['llm_query_model'] = LLM_QUERY_MODEL

        self.feature['embeddings'] = embedding_host is not None and embedding_api_key is not None
        self.feature['llm'] = LLM_PROVIDER_API_KEY is not None

        if system_license:
            self.feature['automation'] = system_license.valid

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



version: Version = Version(version=VERSION, name=TENANT_NAME, production=PRODUCTION, multi_tenant=MULTI_TENANT)
