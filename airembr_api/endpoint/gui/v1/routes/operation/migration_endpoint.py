import os

import alembic.config

from fastapi import APIRouter, Depends

from airembr_api.endpoint.gui.v1.tools.auth.permissions import Permissions
from airembr.system.process.logging.log_handler import get_logger
from airembr.system.config.sys_config import sys_config

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["maintainer"]))]
)

logger = get_logger(__name__)
_local_path = os.path.dirname(__file__)


@router.post("/v1/system/migration/metastore/upgrade", tags=["v1/migration"], include_in_schema=sys_config.expose_gui_api)
def run_mysql_migration_script():
    os.chdir(os.path.realpath(f"{_local_path}/.."))
    alembicArgs = ['--raiseerr', 'upgrade', 'head']
    alembic.config.main(argv=alembicArgs)
