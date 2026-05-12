from srd.domain.table import Table

from airembr.model.system.context import get_context
from airembr.model.system.version import APP_NAME

# TODO not used
def context_database_name(tenant: str, production: bool) -> str:
    mode = "prod" if production else "test"
    return f"bd_{tenant}_{APP_NAME}_{mode}"


def current_bd_database_name() -> str:
    context = get_context()
    return context_database_name(context.tenant, context.production)


class ContextTable(Table):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.database = current_bd_database_name()
