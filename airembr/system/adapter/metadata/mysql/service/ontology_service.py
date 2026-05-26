from airembr.model.metadata.sys_ontology import Ontology
from airembr.system.adapter.metadata.mysql.mapping.ontology_mapping import map_to_ontology, map_to_ontology_table
from airembr.system.adapter.metadata.mysql.schema.table import OntologyTable
from airembr.sdk.storage.metadata.proxy.table_service_proxy import TableServiceProxy
from airembr.sdk.storage.metadata.query.select_result import SelectResult


class OntologyService:

    def __init__(self):
        self.proxy = TableServiceProxy()

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        return await self.proxy.load_all_in_deployment_mode(OntologyTable, search, limit, offset)

    async def load_by_id(self, ontology_id: str) -> SelectResult:
        return await self.proxy.load_by_id_in_deployment_mode(OntologyTable, primary_id=ontology_id)

    async def delete_by_id(self, ontology_id: str):
        return await self.proxy.delete_by_id_in_deployment_mode(
            OntologyTable,
            map_to_ontology,
            primary_id=ontology_id
        )

    async def insert(self, ontology: Ontology):
        return await self.proxy.replace(OntologyTable, map_to_ontology_table(ontology))
