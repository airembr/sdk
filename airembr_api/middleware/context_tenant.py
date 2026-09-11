import os
import re
from typing import Optional, Tuple
from urllib.parse import urlparse

from airembr.system.config.sys_config import sys_config
from airembr.system.process.logging.log_handler import get_logger
from airembr.system.decorator.function_memory_cache import cache_for
from airembr.core.file.file_loaders import pre_config_file_loader

logger = get_logger(__name__)

script_directory = os.path.dirname(os.path.abspath(__file__))
aliases_path = os.path.abspath(os.path.join(script_directory, '../storage/preconfig/data/tenant-aliases.json'))

tenant_aliases = pre_config_file_loader(aliases_path)


def _is_not_ip_url(url: str) -> bool:
    pattern = r"^https?://"  # Schema: http or https
    pattern += r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"  # IPv4 address
    pattern += r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"  # Last octet of the IP
    pattern += r"(:\d+)?(/[\w\-./?%&=]*)?$"  # Optional port and path

    if re.match(pattern, url, re.IGNORECASE):
        return False
    else:
        return True


def _get_hostname_from_scope(scope) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    path = None
    hostname = None
    referer = None
    x_tenant = None

    if 'headers' in scope:
        headers = {item[0].decode(): item[1].decode() for item in scope['headers']}

        scheme = headers.get('scheme', 'http')
        if 'path' in scope:
            path = scope['path']
        if 'referer' in headers:
            referer = headers['referer']
        if 'host' in headers:
            hostname = headers['host']
            hostname = f"{scheme}://{hostname}"
        x_tenant = headers.get('x-tenant', None)

    return hostname, path, referer, x_tenant


@cache_for(3600, key_func=_get_hostname_from_scope, use_context=False)
def get_tenant_name_from_scope(scope) -> Tuple[Optional[str], Optional[str]]:
    hostname, path, referer, x_tenant = _get_hostname_from_scope(scope)

    tenant = None
    if not sys_config.multi_tenant:
        tenant = sys_config.version.name
    elif x_tenant is not None:
        # Priority takes the x-header
        tenant = x_tenant
    elif hostname is not None and _is_not_ip_url(hostname):
        host = urlparse(hostname)
        domain = host.netloc.split(":")[0]  # type: str
        parts = domain.split(".")
        if len(parts) >= 3:
            tenant = parts[0]
            # If tenant is an alias then convert to tenant ID, otherwise leave it as is.
            if isinstance(tenant_aliases, dict):
                tenant = tenant_aliases.get(tenant, tenant)

    if tenant is None or len(tenant) < 3:
        return None, None

    return tenant, hostname
