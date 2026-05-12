from airembr.model.system.named_entity import NamedEntity
from airembr.model.system.context import get_context
from airembr.system.adapter.metadata.mysql.schema.table import EmbeddingTable
from airembr.model.metadata.sys_embedding_setting import EmbeddingSetting
from airembr.system.adapter.metadata.mysql.mapping.utils import split_list


def map_to_embedding_table(embedding: EmbeddingSetting) -> EmbeddingTable:
    context = get_context()

    return EmbeddingTable(
        tenant=context.tenant,
        production=context.production,

        id=embedding.id,
        timestamp=embedding.timestamp,
        name=embedding.name,
        description=embedding.description or "",
        event_type_id=embedding.event_type.id,
        event_type_name=embedding.event_type.name,
        enabled=embedding.enabled,
        tags=','.join(embedding.tags) if embedding.tags else None,
        source_id=embedding.source.id,
        source_name=embedding.source.name
    )


def map_to_embedding(table: EmbeddingTable) -> EmbeddingSetting:
    return EmbeddingSetting(
        production=table.production,
        running=table.running,
        id=table.id,
        timestamp=table.timestamp,
        name=table.name,
        description=table.description or "",
        event_type=NamedEntity(
            id=table.event_type_id or "",
            name=table.event_type_name or ""
        ),
        enabled=table.enabled,
        tags=split_list(table.tags),
        source=NamedEntity(
            id=table.source_id or "",
            name=table.source_name or ""
        ),
    )
