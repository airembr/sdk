from typing import Tuple

from airembr.system.adapter.metadata.mysql.interface import ontology_dao


async def list_ontologies(query: str, limit: int, start: int, output: str) -> Tuple[list, int]:
    return await ontology_dao.load_all_ontologies(query, limit=limit, start=start, output=output)
