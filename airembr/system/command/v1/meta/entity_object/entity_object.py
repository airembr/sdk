from typing import Optional

from airembr.model.entity_object import EntityObject
from airembr.system.adapter.metadata.mysql.interface import entity_object_dao


async def save_entity_object(entity_object: EntityObject):
    if not entity_object.table:
        entity_object.remove_property_columns()

    # Clear from the FK that cannot be saved
    allowed_properties = {prop.name for prop in entity_object.properties if prop.name}
    allowed_stitches = [stitch for stitch in entity_object.stitches if stitch.entity_property in allowed_properties]
    entity_object.stitches = allowed_stitches

    await entity_object_dao.insert(entity_object)


async def get_entity_object_payload(entity_type_id: str) -> Optional[EntityObject]:
    entity_type_id = entity_type_id.lower()
    return await entity_object_dao.load_entity_type_by_id(entity_type_id)


async def delete_entity_object(entity_type_id: str):
    return await entity_object_dao.delete_by_id(entity_type_id)
