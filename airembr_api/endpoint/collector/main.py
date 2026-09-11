import os
import traceback
from time import time
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, Response

from airembr.model.system.header_schema import X_CONTEXT, X_TRACE_ID
from airembr_api.endpoint.collector.routes import collector_endpoint
from airembr_api.endpoint.collector.routes import auth_endpoint
from airembr_api.middleware.context import ContextRequestMiddleware
from airembr_api.service.startup import app_lifespan

from airembr.model.system.context import get_context
from airembr.system.config.global_config import global_settings
from airembr.system.config.server_config import server_config
from airembr.system.config.sys_config import sys_config
from airembr.system.process.logging.log_handler import get_logger
from airembr.system.process.logging import extra_info
from airembr.system.process.logging.log_format_adapter import log_format_adapter

# Conditional
if global_settings.enable_prometheus:
    from airembr.system.process.monitoring.metrics.metrics import REQUEST_COUNT, REQUEST_LATENCY
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

logger = get_logger(__name__)
_local_dir = os.path.dirname(__file__)

sys_config.enable_global_settings = False

application = FastAPI(
    lifespan=app_lifespan,
    title="AiRembr Collector",
    version=str(sys_config.version),
    docs_url='/docs' if server_config.api_docs else None,
    redoc_url=None,
)

application.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


application.include_router(collector_endpoint.router)
application.include_router(auth_endpoint.router)

if global_settings.enable_prometheus:
    @application.get("/metrics", tags=['monitoring'])
    def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


_log_format_adapter = log_format_adapter()


@application.middleware("http")
async def add_process_time_header(request: Request, call_next):
    try:
        start_time = time()

        # Todo Here throttler
        response = await call_next(request)

        if X_CONTEXT in request.headers:
            response.headers[X_CONTEXT] = request.headers.get(X_CONTEXT)

        if X_TRACE_ID in request.headers:
            response.headers[X_TRACE_ID] = request.headers.get(X_TRACE_ID)
        else:
            response.headers[X_TRACE_ID] = get_context().trace_id

        # Prometheus metrics
        process_time = time() - start_time
        if global_settings.enable_prometheus:
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
            ).inc()

            REQUEST_LATENCY.labels(
                endpoint=request.url.path
            ).observe(process_time)

        response.headers["X-Process-Time"] = str(process_time)
        if response.status_code not in [200, 201, 202, 203]:
            logger.stat(f"[{response.status_code}] {request.method} {request.url.path} finished in {process_time}",
                         extra=extra_info.build(origin='Collector API', error_number='API-0001'))
        else:
            logger.stat(f"[{response.status_code}] {request.method} {request.url.path} finished in {process_time}",
                        extra=extra_info.build(origin='Collector API', error_number='API-0001'))

        return response

    except PermissionError as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=403,
            headers={
                "access-control-allow-credentials": "true",
                "access-control-allow-origin": "*"
            },
            content={"detail": str(e)}
        )

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
# Must be after add_process_time_header - so it is executed first
application.add_middleware(ContextRequestMiddleware)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("airembr_api.endpoint.collector.main:application",
                host="0.0.0.0",
                port=4002,
                log_level=server_config.server_logging_level, workers=1)
