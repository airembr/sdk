from airembr.system.adapter.metadata.mysql.service.mysql_installation import wait_for_mysql_connection
from airembr.system.adapter.metadata.sqlite.installation.sqlite_installation import wait_for_sqlite_connection
from airembr.system.config.sys_config import sys_config


async def wait_for_metadata_store():
    if sys_config.meta_data_adapter == 'mysql':
        await wait_for_mysql_connection()
    else:
        wait_for_sqlite_connection()



