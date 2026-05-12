from airembr.system.adapter.metadata.mysql.utils.serilizer import from_model, to_model
from airembr.model.system.context import get_context
from airembr.model.metadata.sys_ent_segment import EntitySegment, TimeConstraint, Actor, Step
from airembr.system.adapter.metadata.mysql.schema.table import SysEntSegmentTable


def map_to_segment_table(segment: EntitySegment) -> SysEntSegmentTable:
    context = get_context()

    return SysEntSegmentTable(
        tenant=context.tenant,
        production=context.production,

        id=segment.id,
        ts=segment.ts,
        name=segment.name,
        description=segment.description or "",
        tags=",".join(segment.tags) if segment.tags else "",
        enabled=segment.enabled,

        time_field = segment.time.field,
        time_start=segment.time.start,
        time_end=segment.time.end,

        entity_type = segment.entity_type,
        entity_where=segment.entity_where,

        sequence=from_model(segment.sequence),
    )


def map_to_segment(table: SysEntSegmentTable) -> EntitySegment:
    return EntitySegment(
        production=table.production,
        running=table.running,
        id=table.id,
        ts=table.ts,
        name=table.name,
        description=table.description or "",
        tags=table.tags.split(",") if table.tags else [],
        enabled=table.enabled,

        time=TimeConstraint(
            field=table.time_field,
            start=table.time_start,
            end=table.time_end
        ),

        entity_type=table.entity_type,
        entity_where=table.entity_where,

        sequence=to_model(table.sequence, Step)
    )
