from typing import Optional, Tuple

from airembr.model.metadata.sys_ontology import Ontology
from airembr.system.adapter.metadata.mysql.interface import ontology_dao


async def list_ontologies(query: str, limit: int, start: int, output: str) -> Tuple[list, int]:
    return await ontology_dao.load_all_ontologies(query, limit=limit, start=start, output=output)


async def get_ontology(ontology_id: str) -> Optional[Ontology]:
    return await ontology_dao.load_ontology_by_id(ontology_id)


async def save_ontology(ontology: Ontology) -> Ontology:
    await ontology_dao.insert_ontology(ontology)
    return ontology


async def delete_ontology(ontology_id: str) -> bool:
    await ontology_dao.delete_ontology_by_id(ontology_id)
    return True
