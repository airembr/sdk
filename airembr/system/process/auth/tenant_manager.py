from typing import Optional, AsyncIterable

from aiohttp import ClientTimeout

from airembr.model.system.tenant import Tenant
from airembr.system.config.sys_config import sys_config
from airembr.sdk.service.remote.http.http_client import HttpClient

class MultiTenantManager:

    def __init__(self):
        self.token = None
        self.auth_endpoint = f"{sys_config.multi_tenant_manager_url}/api-key"
        self.tenants_endpoint = f"{sys_config.multi_tenant_manager_url}/tenant"
        self.tenant_endpoint = f"{sys_config.multi_tenant_manager_url}/tenant"

    async def authorize(self, api_key, timeout=10):

        async with HttpClient(
                3,
                200,
                headers={
                    "Content-Type": "application/json"
                },
                timeout=ClientTimeout(timeout)
        ) as client:
            endpoint = f"{self.auth_endpoint}/{api_key}"
            async with client.get(url=endpoint) as response:
                result = await response.json()

                if response.status != 200:
                    raise PermissionError(f"Can not authorize Multi Tenant Manager at "
                                          f"{self.auth_endpoint}: {result['detail']}. ")

                if 'access_token' not in result:
                    raise PermissionError(
                        "Could not load access token. Are you sure you are connected to the right URL.")

                self.token = result['access_token']

    async def is_tenant_allowed(self, tenant) -> Optional[Tenant]:

        if self.token is None:
            raise PermissionError("You are not authorized to use Multi Tenant Manager API")
        url = f"{self.tenant_endpoint}/{tenant}"

        async with HttpClient(
                3,
                200,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                }
        ) as client:

            async with client.get(url=url) as response:
                result = await response.json()
                if response.status != 200:
                    raise PermissionError(result['detail'])

                tenant = await response.json()
                if tenant:
                    return Tenant(**tenant)

        return None

    async def list_tenants(self) -> AsyncIterable[Tenant]:
        if self.token is None:
            raise PermissionError("You are not authorized to use Multi Tenant Manager API")

        async with HttpClient(
                3,
                200,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                }
        ) as client:
            async with client.get(url=f"{self.tenants_endpoint}") as response:
                result = await response.json()
                if response.status != 200:
                    raise PermissionError(result.get('detail', "Unknown error"))

                for tenant in await response.json():
                    yield Tenant(**tenant)

