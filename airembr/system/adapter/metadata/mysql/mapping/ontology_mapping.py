from airembr.model.metadata.sys_ontology import Ontology
from airembr.model.system.context import get_context
from airembr.system.adapter.metadata.mysql.schema.table import OntologyTable


def map_to_ontology_table(ontology: Ontology) -> OntologyTable:
    context = get_context()
    return OntologyTable(
        id=ontology.id,
        tenant=context.tenant,
        production=context.production,
        name=ontology.name,
        url=ontology.url,
        view=ontology.view,
    )


def map_to_ontology(table: OntologyTable) -> Ontology:
    return Ontology(
        id=table.id,
        production=table.production,
        running=table.running,
        name=table.name,
        url=table.url,
        view=table.view,
    )
