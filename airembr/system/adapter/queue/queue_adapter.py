from airembr.system.config.sys_config import sys_config
from pararun_adapter.adaper_selector import DeferAdapterSelector
from pararun.model.adapter import Adapter

selector = DeferAdapterSelector()

def queue_adapter(adapter_name: str = None) -> Adapter:
    if adapter_name is None:
        raise ValueError("Queue adapter name is required. SET CONSUMER_TYPE env if you are running a worker.")
    return selector.get(adapter_name, queue_tenant=sys_config.queue_tenant)