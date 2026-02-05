from airembr.sdk.model.context import get_context
from airembr.sdk.model.version import APP_NAME


def current_md_database_name() -> str:
    context = get_context()
    return f"md_{context.tenant}_{APP_NAME}"