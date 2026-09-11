from typing import Tuple
from uuid import uuid4

from airembr.model.system.context import get_context
from airembr.model.system.installer.credentials import Credentials
from airembr.model.system.tenant import TenantCredentials, Tenant
from airembr.sdk.service.remote.http.http_client import HttpClient
from airembr.system.command.tenant.errors import TenantInstallError
from airembr.system.config.sys_config import sys_config
from airembr.system.process.installation.installer import install_system


async def install_tenant(tenant_creds: TenantCredentials) -> Tuple[int, dict]:
    if not sys_config.multi_tenant:
        raise TenantInstallError("This tracardi setup is not configured as multi-tenant.", 403)

    context = get_context()
    if tenant_creds.name != context.tenant:
        raise TenantInstallError(f"Can not install tenant `{tenant_creds.name}` on "
                                  f"`{context.tenant}` instance. Please change the URL to match "
                                  f"`{tenant_creds.name}`. Current url is {context.host} and does "
                                  f"not start with `{tenant_creds.name}`.", 403)

    # Authenticate

    try:
        auth_endpoint = f"{sys_config.multi_tenant_manager_url}/api-key/{tenant_creds.tms_api_key}"
        async with HttpClient(3, 200) as client:
            async with client.get(auth_endpoint) as res:
                if res.status != 200:
                    result = await res.json()
                    return res.status, dict(result)

                result = await res.json()
    except Exception as e:
        raise TenantInstallError(f"Error during the connection to TMS. Details: {str(e)}", 403)

    if 'access_token' not in result:
        raise TenantInstallError("No token returned", 403)

    # Create tenant

    token = result['access_token']
    install_token = str(uuid4())

    tenant = Tenant(
        id=context.tenant,
        name=tenant_creds.name,
        email=tenant_creds.email,
        install_token=install_token
    )

    tenant_endpoint = f"{sys_config.multi_tenant_manager_url}/tenant"
    async with HttpClient(3, 200) as client:
        async with client.post(
                tenant_endpoint,
                headers={
                    "accept": "application/json",
                    "Authorization": f"Bearer {token}"},
                json=tenant.model_dump()
        ) as res:
            status = res.status

    if status != 200:
        raise RuntimeError("TMS did not confirmed tenant creation.")

    # Install
    credentials = Credentials(
        username=tenant_creds.email,
        password=tenant_creds.password,
        token=install_token,
        needs_admin=tenant_creds.needs_admin,
        update_mapping=tenant_creds.update_mapping
    )
    return 200, await install_system(credentials)
