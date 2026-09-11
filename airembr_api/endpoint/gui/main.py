import os
import traceback

from airembr.system.license.license_verifier import system_license
from airembr_api.endpoint.gui.routes.data import actor_endpoint, log_endpoint, event_endpoint, autocomplete_endpoint, \
    entity_endpoint, observation_endpoint
from airembr_api.endpoint.gui.routes.pill import pill_endpoint
from airembr_api.middleware.context import ContextRequestMiddleware
from airembr_api.service.startup import app_lifespan

from starlette.responses import JSONResponse
from time import time
from airembr.system.config.server_config import server_config
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from airembr.system.process.logging.log_format_adapter import log_format_adapter
from starlette.staticfiles import StaticFiles
from airembr_api.endpoint.gui.routes import settings_endpoint, metadata_endpoint, \
    deploy_endpoint, tenant_install_endpoint, embedding_setting_endpoint
from airembr_api.endpoint.gui.routes import event_reshaping_schema_endpoint, \
    event_validator_endpoint, console_log_endpoint, import_endpoint, resource_endpoint, \
    dashboard_endpoint, task_endpoint, eql_endpoint, user_account_endpoint, debug_endpoint, user_endpoint, \
    entity_object_endpoint, timer_endpoint, segment_endpoint, canonical_entity_endpoint, ontology_endpoint
from airembr_api.endpoint.gui.routes.mapping import event_mapping_endpoint
from airembr_api.endpoint.gui.routes.management import configuration_endpoint, info_endpoint, \
    health_endpoint, migration_endpoint
from airembr_api.endpoint.gui.routes.install import install_endpoint
from airembr_api.endpoint.gui.routes.outbound import destination_endpoint
from airembr_api.endpoint.gui.routes.inbound import event_source_endpoint, bridge_endpoint
from airembr_api.endpoint.gui.routes.gui import setting_endpoint, feed_endpoint

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
application.include_router(resource_endpoint.router)
application.include_router(event_endpoint.router)
application.include_router(pill_endpoint.router)
application.include_router(autocomplete_endpoint.router)
application.include_router(user_endpoint.auth_router)
application.include_router(health_endpoint.router)
application.include_router(dashboard_endpoint.router)
application.include_router(settings_endpoint.router)
application.include_router(info_endpoint.router)
application.include_router(user_endpoint.router)
application.include_router(event_source_endpoint.router)
application.include_router(debug_endpoint.router)
application.include_router(destination_endpoint.router)
application.include_router(user_account_endpoint.router)
application.include_router(install_endpoint.router)
application.include_router(import_endpoint.router)
application.include_router(task_endpoint.router)
application.include_router(migration_endpoint.router)
application.include_router(event_reshaping_schema_endpoint.router)
application.include_router(event_validator_endpoint.router)
application.include_router(console_log_endpoint.router)
application.include_router(event_mapping_endpoint.router)
application.include_router(bridge_endpoint.router)
application.include_router(entity_endpoint.router)

application.include_router(setting_endpoint.router)
application.include_router(deploy_endpoint.router)
application.include_router(configuration_endpoint.router)
application.include_router(feed_endpoint.router)
application.include_router(metadata_endpoint.router)
application.include_router(dashboard_endpoint.router)
application.include_router(actor_endpoint.router)
application.include_router(log_endpoint.router)
application.include_router(entity_object_endpoint.router)
application.include_router(canonical_entity_endpoint.router)
application.include_router(ontology_endpoint.router)
application.include_router(timer_endpoint.router)
application.include_router(segment_endpoint.router)
application.include_router(embedding_setting_endpoint.router)

application.include_router(tenant_install_endpoint.router)

application.include_router(observation_endpoint.router)

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
