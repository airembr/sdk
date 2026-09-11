import os


def _get_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


AIREMBR_COLLECTOR_URL = os.environ.get("AIREMBR_COLLECTOR_URL", "http://localhost:4002")
AIREMBR_GUI_API_URL = os.environ.get("AIREMBR_GUI_API_URL", "http://localhost:4001")

AIREMBR_COLLECTOR_SHARED_SECRET = os.environ.get("AIREMBR_COLLECTOR_SHARED_SECRET")
AIREMBR_GUI_USERNAME = os.environ.get("AIREMBR_GUI_USERNAME")
AIREMBR_GUI_PASSWORD = os.environ.get("AIREMBR_GUI_PASSWORD")

AIREMBR_TENANT = os.environ.get("AIREMBR_TENANT")
AIREMBR_CONTEXT = os.environ.get("AIREMBR_CONTEXT")
AIREMBR_SOURCE_ID = os.environ.get("AIREMBR_SOURCE_ID", "claude-code")

MCP_TRANSPORT = os.environ.get("MCP_TRANSPORT", "streamable-http")
MCP_HOST = os.environ.get("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.environ.get("MCP_PORT", "8800"))
MCP_SERVER_NAME = os.environ.get("MCP_SERVER_NAME", "airembr-memory")

X_REALTIME = _get_bool("X_REALTIME", False)
REALTIME_ALL = "collect,store,store-observation,destination,logs"
