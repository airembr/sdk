
from fastapi import APIRouter, Depends

from airembr_api.endpoint.gui.auth.permissions import Permissions
from airembr.system.config.sys_config import sys_config
from airembr.system.process.logging.log_handler import get_logger

logger = get_logger(__name__)

router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin"]))]
)


@router.get("/enhancer/source/{type}", tags=["enhancer"], include_in_schema=sys_config.expose_gui_api)
async def get_not_enhanced_profile_records(type: str):

    if type == 'email':
        query: dict = {
            "size": 0,
            "query": {
                "bool": {
                    "must": []
                }
            },
        }

