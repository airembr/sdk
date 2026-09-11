from typing import Optional, List

from airembr.core.data.chunker import chunk_generator
from airembr.model.bigdata.flat_fact import FlatFact
from airembr.system.adapter.bigdata.big_data_adapter import bd_event_adapter, bd_text_adapter
from airembr.system.adapter.bigdata.general.utils.mapping import event_mapping


async def import_texts(rows: List[dict]):
    return await bd_event_adapter.stream(rows)


async def count_facts_by_source(source_id: str):
    return await bd_event_adapter.count_export_facts_by_source(source_id)


async def count_texts_by_source(source_id: str):
    return await bd_text_adapter.count_texts_by_source_id(source_id)


async def export_texts_by_source(source_id: str, page: Optional[int], page_size: Optional[int]) -> list:
    page_size = page_size or 5000
    if page is not None:
        start = page_size * page
        limit = page_size
    else:
        start = 0
        limit = page_size

    result = await bd_text_adapter.load_texts_by_source_id(source_id, start, limit)
    return result.list()


async def export_facts_by_source(source_id: str, page: Optional[int]) -> dict:
    page_size = 5000
    if page is not None:
        start = page_size * page
        limit = page_size
    else:
        start = 0
        limit = page_size

    facts = await bd_event_adapter.export_facts_by_source(source_id, start, limit)
    facts = facts.list()

    sys_evt_map = event_mapping()
    entity_hids = set()
    ACTOR_HID_FILED = sys_evt_map | FlatFact.ACTOR_HID
    OBJECT_HID_FILED = sys_evt_map | FlatFact.OBJECT_HID
    REL_HID = sys_evt_map | FlatFact.REL_HID

    for fact in facts:
        actor_hid = fact.get(ACTOR_HID_FILED, None)
        object_hid = fact.get(OBJECT_HID_FILED, None)
        rel_hid = fact.get(REL_HID, None)

        if actor_hid:
            entity_hids.add(actor_hid)
        if object_hid:
            entity_hids.add(object_hid)
        if rel_hid:
            entity_hids.add(rel_hid)

    entity_objects = []
    for hid_chunk in chunk_generator(entity_hids, 1000, True):
        ents = await bd_event_adapter.export_facts_entities(entities=hid_chunk)
        for ent in ents:
            entity_objects.append(
                {
                    "hid": ent['entity_hid'],  # TODO could be mapped to table
                    "traits": ent['entity_traits'],
                }
            )

    return {"total": page_size, "facts": facts, "entities": entity_objects}
