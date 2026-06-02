from typing import List

from airembr.system.adapter.bigdata.adapter_router import AdapterRouter
from airembr.system.adapter.bigdata.general.utils.mapping import sys_text_mapping
from airembr.system.adapter.bigdata.starrocks.utils.sql_text import load_not_embedded_texts_sql, load_all_texts_sql, \
    load_not_summarized_texts_sql, load_texts_by_source_sql, count_texts_by_source_sql, count_not_summarized_texts_sql, \
    count_not_embedded_texts_sql, count_no_ner_texts_sql, load_no_ner_texts_sql, update_required_ner_texts_sql


class StarrocksTextAdapter(AdapterRouter):

    async def stream(self, rows: List):
        if rows:
            mapping = sys_text_mapping()
            return await self.adapter.stream(rows, mapping)
        return None

    async def count_texts_by_source_id(self, source_id: str):
        sql = count_texts_by_source_sql(source_id)
        result = await self.adapter.exec(sql)
        return result.first().column(0)

    async def load_texts_by_source_id(self, source_id: str, start: int = 0, limit: int = 1000):
        sql = load_texts_by_source_sql(source_id, start, limit)
        return await self.adapter.exec(sql)

    async def count_not_embedded_tests(self):
        sql = count_not_embedded_texts_sql()
        result = await self.adapter.exec(sql)
        return result.first().column(0)

    async def load_not_embedded_tests(self):
        sql = load_not_embedded_texts_sql()
        print(1, sql.literal())
        return await self.adapter.exec(sql)

    async def load_not_summarized_tests(self):
        sql = load_not_summarized_texts_sql()

        return await self.adapter.exec(sql)

    async def count_not_summarized_texts(self):
        sql = count_not_summarized_texts_sql()
        result = await self.adapter.exec(sql)
        return result.first().column(0)

    async def count_no_ner_texts(self):
        sql = count_no_ner_texts_sql()
        result = await self.adapter.exec(sql)
        return result.first().column(0)

    async def load_no_ner_texts(self):
        sql = load_no_ner_texts_sql()
        return await self.adapter.exec(sql)

    async def update_required_ner_texts(self, text_id: str):
        sql = update_required_ner_texts_sql(text_id)
        return await self.adapter.exec(sql)

    async def load_all_texts(self):
        sql = load_all_texts_sql()
        return await self.adapter.exec(sql)
