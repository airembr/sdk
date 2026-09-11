from typing import Optional

from airembr.core.package.invoker import import_package, load_callable, is_coroutine
from airembr.system.command.plugin.errors import PluginError
from dagor.domain.config_validation_payload import ConfigValidationPayload
from dagor.interface.plugin.entrypoint import validate_plugin_configuration


async def call_plugin_helper(module: str, endpoint_function: str, body: dict):
    """
    Calls helper method from Endpoint class in plugin's module
    """

    if not module.startswith('tracardi.process_engine') and not module.startswith('com_tracardi.action'):
        raise PluginError("This is not helper endpoint.", 404)

    module_obj = import_package(module)
    endpoint_module = load_callable(module_obj, 'Endpoint')
    function_to_call = getattr(endpoint_module, endpoint_function)

    if is_coroutine(function_to_call):
        return await function_to_call(body)
    return function_to_call(body)


async def check_plugin_configuration(plugin_id: str, config: Optional[ConfigValidationPayload]):
    return await validate_plugin_configuration(plugin_id, config)
