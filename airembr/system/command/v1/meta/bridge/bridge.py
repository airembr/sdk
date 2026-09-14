from airembr.sdk.storage.metadata.proxy.database_service_proxy import DatabaseServiceProxy
from airembr.system.adapter.metadata.mysql.mapping.bridge_mapping import map_to_bridge
from airembr.system.adapter.metadata.mysql.service.bridge_service import BridgeService
from airembr.system.preconfig.setup_bridges import os_default_bridges


async def reinstall_bridges():
    ds = DatabaseServiceProxy()
    await ds.bootstrap()

    await BridgeService.reinstall(default_bridges=os_default_bridges)


async def get_data_bridges() -> dict:
    """
    Returns list of available data bridges
    """
    bs = BridgeService()
    results = await bs.load_all()
    result = list(results.map_to_objects(map_to_bridge))
    return {
        "total": len(result),
        "result": result
    }


async def get_data_bridges_meta() -> dict:
    """
    Returns list of available data bridges
    """

    bs = BridgeService()
    results = await bs.load_all()

    result = [
        {
            "id": bridge.id,
            "name": bridge.name,
            "type": bridge.type,
            "manual": bridge.manual
        } for bridge in results.rows
    ]

    # Todo then remove the sorting

    return {
        "total": len(result),
        "result": sorted(result, key=lambda x: x['name'])
    }


async def get_data_bridge_by_id(bridge_id: str):
    """
    Returns data bridge
    """
    bs = BridgeService()
    result = await bs.load_by_id(bridge_id)
    return result.map_to_object(map_to_bridge)
