from airembr.system.adapter.bigdata.big_data_adapter import bd_observation_adapter


async def get_observation(observation_id: str) -> list:
    observation_id = observation_id.strip()
    result = await bd_observation_adapter.load_observation_by_id(observation_id)
    return result.list()


async def delete_observation(observation_id: str):
    observation_id = observation_id.strip()
    await bd_observation_adapter.delete_observation_by_id(observation_id)
