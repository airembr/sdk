import asyncio
import os
from typing import Tuple, Dict

from srd.utils.file import read_file

from airembr.model.system.context import ServerContext, get_context
from airembr.system.process.logging import extra_info
from airembr.system.process.logging.log_handler import get_installation_logger
from airembr.system.adapter.bigdata.starrocks.starrocks_base_adapter import StarrocksBaseAdapter
from airembr.model.system.installer.credentials import Credentials
from airembr.system.config.sys_config import sys_config

from airembr.system.adapter.bigdata.env.bigdata_context import current_bd_database_name
from airembr.system.schema.resource import Resource
from airembr.system.process.auth.tenant_manager import MultiTenantManager

logger = get_installation_logger(__name__)
_installed_tenants: Dict[str, bool] = {}
_resource = Resource()
_local_dir = os.path.dirname(__file__)


def _get_missing(tables, type) -> list:
    return [idx[1] for idx in tables if idx[0] == type]


def _get_sql(sql_file: str):
    return read_file(sql_file)


class StarrocksInstallAdapter(StarrocksBaseAdapter):

    async def _get_tables_status(self, database: str):
        for table in _resource.get_tenant_table_names():
            if await self._client.table_exists(table, database):
                yield "existing_table", table
            else:
                yield "missing_table", table

    async def _schema_exists(self):
        with ServerContext(get_context().switch_context(production=False)) as cm:
            if not await self.client.database_schema_exists(current_bd_database_name()):
                return False
        with ServerContext(get_context().switch_context(production=True)) as cm:
            if not await self.client.database_schema_exists(current_bd_database_name()):
                return False

        return True

    async def is_big_data_schema_ok(self) -> Tuple[bool, list]:

        is_schema_ok = await self._schema_exists()

        if not is_schema_ok:
            return False, []

        # Missing tables in staging
        with ServerContext(get_context().switch_context(production=False)):
            _tables_staging = [item async for item in self._get_tables_status(current_bd_database_name())]

        # Missing tables in production
        with ServerContext(get_context().switch_context(production=True)):
            _tables_production = [item async for item in self._get_tables_status(current_bd_database_name())]

        _tables = _tables_staging + _tables_production

        missing_tables = _get_missing(_tables, type='missing_table')

        is_schema_ok = not missing_tables

        if not is_schema_ok:
            logger.warning(f"Missing schemas: Tables {missing_tables}")

        return is_schema_ok, _tables

    async def wait_for_connection(self, no_of_tries=10, wait_between=5):
        success = False
        host = self._client.client.config.starrocks_host
        port = self._client.client.config.starrocks_port
        user = self._client.client.config.starrocks_username
        database = 'sys'

        while True:
            try:

                if no_of_tries < 0:
                    break

                await self._client.test_connection(database)
                success = True
                break

            except ConnectionRefusedError as e:
                no_of_tries -= 1

                logger.warning(
                    f"Could not connect to starrocks at {user}@{host}:{port} (db: {database}). Number of tries left: {no_of_tries}. "
                    f"Waiting 5s before retry. Error details: {str(e)}")
                if host == 'localhost':
                    logger.warning("You are trying to connect to 127.0.0.1. If this instance is running inside docker "
                                   "then you can not use localhost as starrocks is probably outside the container. Use "
                                   "external IP that docker can connect to.")
                await asyncio.sleep(wait_between)

            # todo check if this is needed when we make a single thread startup.
            except Exception as e:
                await asyncio.sleep(1)
                no_of_tries -= 1
                logger.error(
                    f"Could not save data. Number of tries left: {no_of_tries}. Waiting 1s to retry. Error details: {repr(e)}",
                    extra=extra_info.exact(origin="Install Adapter", error_number="E-0022", package=__name__))

        if success:
            logger.dev_info(f"Connected to starrocks at {host}")
            return

        logger.error(f"Could not connect to starrocks at {host}",
                     extra=extra_info.exact(origin="Install Adapter", error_number="E-0023", package=__name__))
        exit(1)

    async def _create_table(self, sql, database_name):
        try:
            await self._client.create_tables(sql, database_name)
        except Exception as e:
            logger.error(f"Could not create table in database: {database_name}. SQL: {sql},  Details: {str(e)}")
            raise e

    async def _enable_vector_support(self):
        try:
            await self._client.create_tables(
                'ADMIN SET FRONTEND CONFIG ("enable_experimental_vector" = "true"); ADMIN SET FRONTEND CONFIG ("enable_experimental_gin" = "true");',
                'sys'
            )
            logger.info("StarRocks vector index support enabled.")
        except Exception as e:
            logger.warning(
                f"Could not enable vector index support. "
                f"If installation fails with a vector index error, run manually: "
                f'ADMIN SET FRONTEND CONFIG ("enable_experimental_vector" = "true"). '
                f"Details: {str(e)}"
            )

    async def install_big_data_database(self, credentials: Credentials):
        if sys_config.multi_tenant:
            context = get_context()
            mtm = MultiTenantManager()
            logger.info(f"Authorizing `{context.tenant}` for installation at {mtm.auth_endpoint}.")

            if not sys_config.multi_tenant_manager_api_key:
                raise PermissionError(f"Installation stopped no Tenant Management API key set.")

            if not sys_config.multi_tenant_manager_url:
                raise PermissionError(f"Installation stopped not Tenant Management API URL set.")

            try:
                await mtm.authorize(sys_config.multi_tenant_manager_api_key)
                tenant = await mtm.is_tenant_allowed(context.tenant)
            except Exception as e:
                raise PermissionError(
                    f"Installation stopped Tenant Management System returned na error when authorizing "
                    f"tenant {context.tenant}: Details {str(e)}.")

            if not tenant:
                raise PermissionError(f"Installation forbidden. Tenant [{context.tenant}] not allowed.")

            logger.info(f"Tenant `{context.tenant}` authorized for installation.")

        if credentials.needs_admin:
            if credentials.empty() or not credentials.username_as_email():
                raise PermissionError("Installation forbidden. Invalid admin account "
                                      "login or password. Login must be a valid email and password "
                                      "can not be empty.")

        _schema = os.path.join(_local_dir, 'installer/schema/')
        # Install staging

        tables = list(_resource.get_create_table_stmts())
        views = list(_resource.get_create_view_stmts('starrocks'))

        await self._enable_vector_support()

        with ServerContext(get_context().switch_context(production=False)) as cm:
            database = current_bd_database_name()
            await self._client.create_database(database)
            for sql in tables:
                await self._create_table(sql, database_name=database)
            for view in views:
                if view:
                    view = view.replace('{|database|}', database)
                    await self._create_table(view, database_name=database)

        # Install production
        with ServerContext(get_context().switch_context(production=True)):
            database = current_bd_database_name()
            await self._client.create_database(database)
            for sql in tables:
                await self._create_table(sql, database_name=database)

            for view in views:
                if view:
                    view = view.replace('{|database|}', database)
                    await self._create_table(view, database_name=database)

        logger.info(f"Installing plugins on startup")

        staging_install_result = {}
        production_install_result = {}

        return staging_install_result, production_install_result

    def get_connection_info(self):
        host = self._client.client.config.starrocks_host
        port = self._client.client.config.starrocks_port
        user = self._client.client.config.starrocks_username
        return 'starrocks', user, host, port

    async def close(self):
        logger.dev_info("Closing connection to starrocks.")
        return await self.client.close()
