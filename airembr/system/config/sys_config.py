from dotenv import load_dotenv
import os

from airembr.system.process.logging import extra_info
from airembr.system.process.logging.log_handler import get_logger
from airembr.system.process.logging.log_level import get_logging_level

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

import logging
from hashlib import md5

from airembr.core.validator.url import is_valid_url
from airembr.core.singleton import Singleton
from airembr.core.env.validator import get_env_as_int, get_env_as_bool
from airembr.model.system.version import version, APP_NAME, VERSION

logger = get_logger(__name__)

class SysConfig(metaclass=Singleton):

    def __init__(self):
        env = os.environ
        self.version = version
        self.app_name = 'airembr'
        self.enable_triggers = get_env_as_bool('ENABLE_TRIGGERS', 'yes')
        self.enable_event_validation = get_env_as_bool('ENABLE_EVENT_VALIDATION', 'yes')
        self.enable_event_reshaping = get_env_as_bool('ENABLE_EVENT_RESHAPING', 'yes')
        self.enable_event_source_check = get_env_as_bool('ENABLE_EVENT_SOURCE_CHECK', 'yes')

        self.disallow_bot_traffic = get_env_as_bool('DISALLOW_BOT_TRAFFIC', 'yes')
        self.enable_async_caching = get_env_as_bool('ENABLE_ASYNC_CACHING', 'no')
        self.enable_global_settings = get_env_as_bool('ENABLE_GLOBAL_SETTINGS', "yes")

        self.logging_level = get_logging_level(env['LOGGING_LEVEL']) if 'LOGGING_LEVEL' in env else logging.WARNING

        self.multi_tenant = version.multi_tenant
        self.multi_tenant_manager_url = env.get('MULTI_TENANT_MANAGER_URL', None)
        self.multi_tenant_manager_api_key = env.get('MULTI_TENANT_MANAGER_API_KEY', None)
        self.expose_gui_api = get_env_as_bool('EXPOSE_GUI_API', 'yes')
        self.image_tag = env.get('IMAGE_TAG', 'n/a')
        self.installation_token = env.get('INSTALLATION_TOKEN', 'airembr')
        random_hash = md5(f"1691ef68-dbc6-47d4-b715-38032b4d331c-{self.version.db_version}".encode()).hexdigest()
        self.internal_source = f"@internal-{random_hash[:20]}"
        self.api_key = env.get('API_KEY', None)

        self.auto_profile_merging = env.get('AUTO_PROFILE_MERGING', 's>a.d-kljsa87^5adh')

        self.maxmind_host = env.get('MAXMIND_HOST', 'geolite.info')
        self.maxmind_license_key: str | None = env.get('MAXMIND_LICENSE_KEY', None)
        self.maxmind_account_id: int | None = get_env_as_int('MAXMIND_ACCOUNT_ID', None)

        self.queue_enabled = get_env_as_bool('QUEUE_ENABLED', 'yes')
        self.queue_tenant = env.get('QUEUE_TENANT', f'{APP_NAME}-{VERSION}')

        # Not used now
        self.dispatch_log_partitioning = env.get('DISPATCH_LOG_PARTITIONING', 'month')
        self.console_log_partitioning = env.get('CONSOLE_LOG_PARTITIONING', 'month')
        self.item_partitioning = env.get('ITEM_PARTITIONING', 'year')
        self.skip_errors_on_profile_mapping = get_env_as_bool('SKIP_ERRORS_ON_PROFILE_MAPPING', 'no')

        self.cache_adapter = env.get('CACHE_ADAPTER', 'redis')
        self.big_data_adapter = env.get('BIG_DATA_ADAPTER', 'starrocks')  # starrocks, duckdb
        self.meta_data_adapter = env.get('META_DATA_ADAPTER', 'mysql')  # sqlite, mysql

        self._config = None

        env['INSTALLATION_TOKEN'] = ""

        if self.multi_tenant_manager_url:
            self.multi_tenant_manager_url = self.multi_tenant_manager_url.strip("/")

        if self.multi_tenant and (self.multi_tenant_manager_url is None or self.multi_tenant_manager_api_key is None):
            if self.multi_tenant_manager_url is None:
                logger.warning('No MULTI_TENANT_MANAGER_URL set for MULTI_TENANT mode. Either set '
                               'the MULTI_TENANT_MANAGER_URL or set MULTI_TENANT to "no"',
                               extra=extra_info.build(object=self, origin="configuration", error_number="C-0001")
                               )

            if self.multi_tenant_manager_api_key is None:
                logger.warning('No MULTI_TENANT_MANAGER_API_KEY set for MULTI_TENANT mode. Either set '
                               'the MULTI_TENANT_MANAGER_API_KEY or set MULTI_TENANT to "no"',
                               extra=extra_info.build(object=self, origin="configuration", error_number="C-0002")
                               )

        if self.multi_tenant and not is_valid_url(self.multi_tenant_manager_url):
            logger.warning('Env MULTI_TENANT_MANAGER_URL is not valid URL.',
                           extra=extra_info.build(object=self, origin="configuration", error_number="C-0003")
                           )

        if not self.api_key or len(self.api_key) < 20:
            logger.warning(
                'Security risk. Env API_KEY not set or too short. It must be at least 20 chars long.',
                extra=extra_info.build(object=self, origin="configuration", error_number="C-0005")
            )

    def is_apm_on(self) -> bool:
        return False

    def has_maxmind_configured(self) -> bool:
        return not (self.maxmind_host is None or self.maxmind_account_id is None or self.maxmind_license_key is None)

    def db_adapter_column_type(self):
        adapter = self.big_data_adapter
        if adapter == 'starrocks':
            return 'sr_column_type'
        else:
            raise ValueError(f"Unknown db adapter type {adapter}")


sys_config = SysConfig()