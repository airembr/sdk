from airembr.system.adapter.bigdata.big_data_adapter import _bd_install_adapter


async def wait_for_bigdata_store():
    await _bd_install_adapter().wait_for_connection()
