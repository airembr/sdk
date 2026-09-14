import os
import traceback
from time import time
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request

from airembr_api.endpoint.pill.routes import pill_endpoint
from airembr_api.middleware.context import ContextRequestMiddleware
from airembr_api.service.startup import app_lifespan

from airembr.system.config.server_config import server_config
from airembr.system.config.sys_config import sys_config
from airembr.system.process.logging.log_handler import get_logger
from airembr.system.process.logging.log_format_adapter import log_format_adapter

logger = get_logger(__name__)
_local_dir = os.path.dirname(__file__)

application = FastAPI(
    lifespan=app_lifespan,
    title="AiRembr Pill",
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

application.include_router(pill_endpoint.router)

_log_format_adapter = log_format_adapter()


@application.middleware("http")
async def add_process_time_header(request: Request, call_next):
    try:
        start_time = time()

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

# Must be after add_process_time_header - so it is executed first
application.add_middleware(ContextRequestMiddleware)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("airembr_api.endpoint.pill.main:application", host="0.0.0.0", port=4003,
                log_level=server_config.server_logging_level,
                workers=1)
