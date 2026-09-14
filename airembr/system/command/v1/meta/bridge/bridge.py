from airembr.system.adapter.metadata.mysql.mapping.bridge_mapping import map_to_bridge
from airembr.system.adapter.metadata.mysql.service.bridge_service import BridgeService


async def get_data_bridge_by_id(bridge_id: str):
    """
    Returns data bridge
    """
    bs = BridgeService()
    result = await bs.load_by_id(bridge_id)
    return result.map_to_object(map_to_bridge)
