import asyncio

from typing import List, Optional
from pydantic import BaseModel

from airembr.sdk.storage.metadata.proxy.database_service_proxy import DatabaseServiceProxy
from airembr.sdk.storage.metadata.proxy.table_service_proxy import TableServiceProxy
from airembr.model.system.context import ServerContext, get_context
from airembr.core.singleton import Singleton
from airembr.system.config.sys_config import sys_config
from airembr.system.logging import extra_info
from airembr.system.logging.log_handler import get_installation_logger
from airembr.system.adapter.bigdata.big_data_adapter import *
from airembr.system.process.auth.tenant_manager import MultiTenantManager

from airembr.system.adapter.metadata.mysql.service.user_service import UserService
from airembr.system.adapter.metadata.mysql.schema.table import UserTable

logger = get_installation_logger(__name__)

async def _check_mysql_db_exists(database):
    ds = DatabaseServiceProxy()
    return await ds.exists(database)


async def _check_sqlite_db_exists(database):
    return True


async def _check_admin_account() -> bool:
    ts = TableServiceProxy()

    if await ts.exists(UserTable.__tablename__):
        with ServerContext(get_context().switch_context(False)):
            us = UserService()
            admin_records = await us.load_by_role('admin')
    else:
        admin_records = []

    return len(admin_records) > 0



async def check_installation() -> dict:
    """
    Returns list of missing and updated indices
    """

    # Check Metadata

    ds = DatabaseServiceProxy()

    database = ds.get_current_md_database_name()
    has_db = ds.exists(database)

    if not await has_db:
        logger.warning("No MetaData Database",
                       exc_info=extra_info.exact(
                           error_number="I-0003",
                           origin="Installation",
                           package=__name__))
        return {
            "schema_ok": False,
            "admin_ok": False,
            "form_ok": False,
            "warning": None
        }


    missing_tables = await ds.inspect(database)
    if missing_tables:
        return {
            "schema_ok": False,
            "admin_ok": 'sys_user' not in missing_tables,
            "form_ok": False,
            "warning": None
        }

    has_admin_account = await _check_admin_account()

    # Big data

    schema_ok, _ = await bd_install_adapter.is_big_data_schema_ok()

    if schema_ok is False:
        return {
            "schema_ok": False,
            "admin_ok": has_admin_account,
            "form_ok": None,
            "warning": None
        }

    if sys_config.multi_tenant and (not schema_ok or not has_admin_account):
        mtm = MultiTenantManager()
        context = get_context()

        logger.info(f"Authorizing `{context.tenant}` for installation at {mtm.auth_endpoint}.")

        try:
            await mtm.authorize(sys_config.multi_tenant_manager_api_key)
        except asyncio.exceptions.TimeoutError:
            message = (f"Authorizing failed for tenant `{context.tenant}`. "
                       f"Could not reach Tenant Management Service.")
            logger.warning(message, exc_info=extra_info.exact(
                error_number="I-0001",
                origin="Installation",
                package=__name__))
            return {
                "schema_ok": False,
                "admin_ok": False,
                "form_ok": False,
                "warning": message
            }

        tenant = await mtm.is_tenant_allowed(context.tenant)
        if not tenant:
            logger.warning(f"Authorizing failed for tenant `{context.tenant}`.",
                           exc_info=extra_info.exact(
                               error_number="I-0002",
                               origin="Installation", package=__name__))
            return {
                "schema_ok": False,
                "admin_ok": False,
                "form_ok": False,
                "warning": f"Tenant [{context.tenant}] not allowed."
            }

    return {
        "schema_ok": schema_ok,
        "admin_ok": has_admin_account,
        "form_ok": True,
        "warning": None
    }


class SystemInstallationStatus(BaseModel):
    schema_ok: bool = False
    admin_ok: Optional[bool] = None
    form_ok: Optional[bool] = None
    warning: Optional[List[str]] = None
    config: Optional[dict] = {}

    @staticmethod
    async def check() -> 'SystemInstallationStatus':
        status = await check_installation()
        return SystemInstallationStatus(**status)


class InstallationStatus(metaclass=Singleton):

    @staticmethod
    async def get_status():
        status = await SystemInstallationStatus.check()
        return {
            "schema": status.schema_ok,
            "users": status.admin_ok,
            "form": status.form_ok
        }


installation_status = InstallationStatus()
