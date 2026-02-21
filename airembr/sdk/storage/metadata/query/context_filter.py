from typing import Type
from sqlalchemy import and_
from airembr.sdk.storage.metadata.db_base import Base


def context_filter(table: Type[Base], tenant: str, production: bool, *clauses):
    def _wrapper():
        return and_(table.tenant == tenant, table.production == production, *clauses)

    return _wrapper