from typing import Optional

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from airembr.model.system.version import version
from airembr.model.system.context import Context, ServerContext
from airembr.system.process.logging import extra_info
from airembr.system.process.logging.log_handler import get_logger
from airembr.system.process.logging.log_manager import save_logs

from api.middleware.context_tenant import get_tenant_name_from_scope
from api.endpoint.gui.auth.user_db import token2user

logger = get_logger(__name__)


def _get_header_value(scope, key) -> Optional[str]:
    headers = scope.get('headers', None)

    if headers:
        for header, value in headers:
            if header.decode() == key:
                return value.decode()

    return None


def _get_context_object(scope) -> Optional[Context]:
    # Default context comes from evn variable PRODUCTION
    production = version.production

    # If env variable set to PRODUCTION=yes there is no way to change it.
    # Production means production. Otherwise the context can be changed
    # form outside.

    tenant, hostname = get_tenant_name_from_scope(scope)
    if not tenant:
        return None

    if not production:  # Staging as default
        context = _get_header_value(scope, "x-context")
        # if has some value
        if context and context in ['production', 'staging']:
            production = context.lower() == 'production'

    # Extract URL and query parameters
    url_path = scope.get("path", "")
    query_params = scope.get("query_string", b"")

    return Context(
        production=production,
        user=None,
        tenant=tenant,
        host=hostname,
        metadata={
            "path": url_path,
            "params": query_params,
            "body": None,
            "headers": scope.get('headers', [])
        }
    )


class ContextRequestMiddleware:
    def __init__(
            self,
            app: ASGIApp,
    ) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ["http", "websocket", "https"]:
            await self.app(scope, receive, send)
            return

        context_object = _get_context_object(scope)
        if not context_object:
            logger.warning(f"Can not find tenant for this URL. Set tenant ID in header.",
                           extra=extra_info.build("context-middleware", object=self, error_number="CRM-0002"))
            # Stop the request here with a direct response
            response = JSONResponse({"detail": f"Unknown tenant context."}, status_code=401)
            await response(scope, receive, send)
            return  # Do NOT call self.app; Request ends here

        with ServerContext(context_object) as cm:
            if scope.get('method', None) != "options":
                token = _get_header_value(scope, 'authorization')
                if token:
                    _, token = token.split()
                    user = token2user.get(token)
                    # This is dangerous user mutation. Never do this in other places.
                    cm.get_context().user = user
            try:
                await self.app(scope, receive, send)
            except Exception as e:
                logger.error(str(e), extra=extra_info.build(
                    "context-middleware",
                    error_number="CRM-0001",
                    object=self,
                ))
                raise e
            finally:
                await save_logs()
