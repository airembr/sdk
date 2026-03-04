from typing import List

import lancedb

from airembr.sdk.common.singleton import Singleton


class LanceVectorDb(metaclass=Singleton):
    def __init__(self):
        DB_PATH = "./_lancedb"
        self.db = lancedb.connect(DB_PATH)

    def index(self, table_name, rows: List[dict]):
        # TODO Index with ArrowTable
        return self.db.create_table(table_name, data=rows)

    def drop(self, table_name: str):
        try:
            self.db.drop_table(table_name)
        except Exception:
            pass
