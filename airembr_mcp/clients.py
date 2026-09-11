import threading
from typing import Any, Callable, Tuple

from airembr_sdk.client.airembr_api import AirembrApi
from airembr_sdk.model.core.value.response_status import QueryStatus

from airembr_mcp import config

_lock = threading.Lock()
_collector_client: AirembrApi | None = None
_gui_client: AirembrApi | None = None


def _authenticate_collector(client: AirembrApi) -> None:
    if config.AIREMBR_COLLECTOR_SHARED_SECRET:
        status, payload = client.authenticate_with_secret(config.AIREMBR_COLLECTOR_SHARED_SECRET)
        if not status.ok():
            raise ConnectionError(f"Collector authentication failed: {status} {payload}")


def _authenticate_gui(client: AirembrApi) -> None:
    if not config.AIREMBR_GUI_USERNAME or not config.AIREMBR_GUI_PASSWORD:
        raise RuntimeError(
            "AIREMBR_GUI_USERNAME and AIREMBR_GUI_PASSWORD must be set to use the ask/search_observations tools."
        )
    status, payload = client.authenticate(config.AIREMBR_GUI_USERNAME, config.AIREMBR_GUI_PASSWORD)
    if not status.ok():
        raise ConnectionError(f"GUI API authentication failed: {status} {payload}")


def get_collector_client() -> AirembrApi:
    global _collector_client
    with _lock:
        if _collector_client is None:
            client = AirembrApi(config.AIREMBR_COLLECTOR_URL, context=config.AIREMBR_CONTEXT,
                                tenant=config.AIREMBR_TENANT)
            _authenticate_collector(client)
            _collector_client = client
        return _collector_client


def get_gui_client() -> AirembrApi:
    global _gui_client
    with _lock:
        if _gui_client is None:
            client = AirembrApi(config.AIREMBR_GUI_API_URL, context=config.AIREMBR_CONTEXT,
                                tenant=config.AIREMBR_TENANT)
            _authenticate_gui(client)
            _gui_client = client
        return _gui_client


def call_with_reauth(client: AirembrApi, fn: Callable[..., Tuple[QueryStatus, Any]],
                     reauth_fn: Callable[[AirembrApi], None], *args, **kwargs) -> Tuple[QueryStatus, Any]:
    status, payload = fn(*args, **kwargs)
    if status == 401:
        reauth_fn(client)
        status, payload = fn(*args, **kwargs)
    return status, payload


def call_collector_with_reauth(fn_name: str, *args, **kwargs) -> Tuple[QueryStatus, Any]:
    client = get_collector_client()
    fn = getattr(client, fn_name)
    return call_with_reauth(client, fn, _authenticate_collector, *args, **kwargs)


def call_gui_with_reauth(fn_name: str, *args, **kwargs) -> Tuple[QueryStatus, Any]:
    client = get_gui_client()
    fn = getattr(client, fn_name)
    return call_with_reauth(client, fn, _authenticate_gui, *args, **kwargs)
