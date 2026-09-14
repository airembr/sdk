import os
import traceback

from airembr.system.license.license_verifier import system_license
from airembr_api.endpoint.gui.routes.data import actor_endpoint, log_endpoint, event_endpoint, autocomplete_endpoint, \
    entity_endpoint, observation_endpoint
from airembr_api.middleware.context import ContextRequestMiddleware
from airembr_api.service.startup import app_lifespan

from starlette.responses import JSONResponse
from time import time
from airembr.system.config.server_config import server_config
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from airembr.system.process.logging.log_format_adapter import log_format_adapter
from starlette.staticfiles import StaticFiles
from airembr_api.endpoint.gui.routes import metadata_endpoint, \
    embedding_setting_endpoint

from airembr_api.endpoint.gui.v1.routes.operation import deploy_endpoint, install_endpoint, health_endpoint, \
    migration_endpoint
from airembr_api.endpoint.gui.routes import payload_reshaping_schema_endpoint, \
    payload_validator_endpoint, console_log_endpoint, dashboard_endpoint, task_endpoint, eql_endpoint, user_endpoint, \
    entity_object_endpoint
from airembr_api.endpoint.gui.routes.mapping import event_mapping_endpoint
from airembr_api.endpoint.gui.routes.management import info_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.feed import crud_endpoint as crud_feed_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.canonical_entity import crud_endpoint as crud_canonical_entity_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.embedding_setting import crud_endpoint as crud_embedding_setting_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.entity_object import crud_endpoint as crud_entity_object_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.reshaping_schema import crud_endpoint as crud_event_reshaping_schema_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.validator import crud_endpoint as crud_event_validator_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.payload_mapping import crud_endpoint as crud_event_mapping_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.ontology import crud_endpoint as crud_ontology_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.destination import crud_endpoint as crud_destination_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.segment import crud_endpoint as crud_segment_endpoint
from airembr_api.endpoint.gui.v1.routes.data.event import crud_endpoint as crud_event_endpoint
from airembr_api.endpoint.gui.v1.routes.data.observation import crud_endpoint as crud_observation_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.task import crud_endpoint as crud_task_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.user import crud_endpoint as crud_user_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.timer import crud_endpoint as timer_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.user_account import crud_endpoint as user_account_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.bridge import crud_endpoint as crud_bridge_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.configuration import crud_endpoint as crud_configuration_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.source import crud_endpoint as crud_source_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.resource import crud_endpoint as crud_resource_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.settings import crud_endpoint as crud_settings_endpoint

# List Endpoints
from airembr_api.endpoint.gui.v1.routes.meta.bridge import list_endpoint as list_bridge_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.configuration import list_endpoint as list_configuration_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.source import list_endpoint as list_source_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.resource import list_endpoint as list_resource_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.ontology import list_endpoint as list_ontology_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.segment import list_endpoint as list_segment_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.canonical_entity import list_endpoint as list_canonical_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.destination_resource import list_endpoint as list_destination_resource_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.destination import list_endpoint as list_destination_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.destination_trigger import list_endpoint as list_destination_trigger_endpoint
from airembr_api.endpoint.gui.v1.routes.meta.settings import list_endpoint as list_settings_endpoint

from airembr.system.config.sys_config import sys_config
from airembr.system.process.logging.log_handler import get_logger

logger = get_logger(__name__)
_local_dir = os.path.dirname(__file__)

application = FastAPI(
    lifespan=app_lifespan,
    title="AirRembr",
    version=str(sys_config.version),
    docs_url='/docs' if server_config.api_docs else None,
    redoc_url='/redoc' if server_config.api_docs else None
)

application.add_middleware(ContextRequestMiddleware)

application.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tracker = os.path.join(_local_dir, "../html/tracker")
if os.path.exists(tracker):
    application.mount("/tracker",
                      StaticFiles(
                          html=True,
                          directory=tracker),
                      name="tracker")
uix = os.path.join(_local_dir, "../html/uix")

if os.path.exists(uix):
    application.mount("/uix",
                      StaticFiles(
                          html=True,
                          directory=uix),
                      name="uix")

application.include_router(eql_endpoint.router)

application.include_router(event_endpoint.router)
application.include_router(autocomplete_endpoint.router)
application.include_router(user_endpoint.auth_router)
application.include_router(dashboard_endpoint.router)
application.include_router(info_endpoint.router)
application.include_router(user_endpoint.router)
application.include_router(user_account_endpoint.router)
application.include_router(task_endpoint.router)
application.include_router(payload_reshaping_schema_endpoint.router)
application.include_router(payload_validator_endpoint.router)
application.include_router(console_log_endpoint.router)
application.include_router(event_mapping_endpoint.router)
application.include_router(entity_endpoint.router)
application.include_router(metadata_endpoint.router)
application.include_router(dashboard_endpoint.router)
application.include_router(actor_endpoint.router)
application.include_router(log_endpoint.router)
application.include_router(entity_object_endpoint.router)
application.include_router(embedding_setting_endpoint.router)

application.include_router(observation_endpoint.router)

# OPERATION routers
application.include_router(health_endpoint.router)
application.include_router(install_endpoint.router)
application.include_router(deploy_endpoint.router)
application.include_router(migration_endpoint.router)

# CRUD routers (airembr_api/endpoint/gui/v1/routes/{meta,data}/<domain>/crud_endpoint.py)
application.include_router(crud_feed_endpoint.router)
application.include_router(crud_canonical_entity_endpoint.router)
application.include_router(crud_embedding_setting_endpoint.router)
application.include_router(crud_entity_object_endpoint.router)
application.include_router(crud_event_reshaping_schema_endpoint.router)
application.include_router(crud_event_validator_endpoint.router)
application.include_router(crud_configuration_endpoint.router)
application.include_router(crud_event_mapping_endpoint.router)
application.include_router(crud_ontology_endpoint.router)
application.include_router(crud_destination_endpoint.router)
application.include_router(crud_resource_endpoint.router)
application.include_router(crud_segment_endpoint.router)
application.include_router(crud_source_endpoint.router)
application.include_router(crud_bridge_endpoint.router)
application.include_router(crud_event_endpoint.router)
application.include_router(crud_observation_endpoint.router)
application.include_router(crud_task_endpoint.router)
application.include_router(crud_user_endpoint.router)
application.include_router(timer_endpoint.router)
application.include_router(crud_settings_endpoint.router)

# LIST routers
application.include_router(list_source_endpoint.router)
application.include_router(list_resource_endpoint.router)
application.include_router(list_configuration_endpoint.router)
application.include_router(list_bridge_endpoint.router)
application.include_router(list_ontology_endpoint.router)
application.include_router(list_segment_endpoint.router)
application.include_router(list_canonical_endpoint.router)
application.include_router(list_destination_resource_endpoint.router)
application.include_router(list_destination_endpoint.router)
application.include_router(list_destination_trigger_endpoint.router)
application.include_router(list_settings_endpoint.router)

_log_format_adapter = log_format_adapter()

# Commercial
if system_license.valid:
    from airembr_api.endpoint.gui.routes.workflow import flow_endpoint, flow_action_endpoint, plugins_endpoint

    application.include_router(flow_action_endpoint.router)
    application.include_router(plugins_endpoint.router)
    application.include_router(flow_endpoint.router)


@application.middleware("http")
async def add_process_time_header(request: Request, call_next):
    try:

        start_time = time()

        # Todo Here throttler

        response = await call_next(request)
        process_time = time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        if 'x-context' in request.headers:
            response.headers["X-Context"] = request.headers.get('x-context')

        return response

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            headers={
                "access-control-allow-credentials": "true",
                "access-control-allow-origin": "*"
            },
            content={"detail": str(e)}
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("airembr_api.endpoint.gui.main:application", host="0.0.0.0", port=4001,
                log_level=server_config.server_logging_level,
                workers=1)
