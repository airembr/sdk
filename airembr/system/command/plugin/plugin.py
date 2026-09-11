from collections import defaultdict
from typing import Optional

from airembr.model.system.enum.yes_no import YesNo
from airembr.model.system.state import Settings
from dagor.interface.plugin.entrypoint import (
    load_plugin, set_plugin_state, list_plugins, install_default_plugins, delete_plugin as dagor_delete_plugin,
)
from airembr.system.command.plugin.errors import PluginError


async def get_plugin(plugin_id: str):
    """
    Returns FlowActionPlugin object.
    """
    plugin = load_plugin(plugin_id)
    if not plugin:
        raise PluginError(f"Missing plugin id '{plugin_id}'", 404)
    return plugin


async def get_plugin_state(plugin_id: str, state: YesNo):
    """
    Returns FlowActionPlugin object.
    """
    return await set_plugin_state(
        plugin_id=plugin_id,
        state_type="settings_hidden",
        state=Settings.as_bool(state)
    )


async def set_plugin_enabled_disabled(plugin_id: str, state: YesNo):
    """
    Sets FlowActionPlugin enabled or disabled.
    """
    return await set_plugin_state(
        plugin_id=plugin_id,
        state_type="settings_enabled",
        state=Settings.as_bool(state)
    )


async def edit_plugin_icon(plugin_id: str, icon: str):
    """
    Edits icon for action with given ID
    """
    return await set_plugin_state(
        plugin_id=plugin_id,
        state_type="plugin_metadata_icon",
        state=icon)


async def edit_plugin_name(plugin_id: str, name: str):
    """
    Edits name for action with given ID
    """
    return await set_plugin_state(
        plugin_id=plugin_id,
        state_type="plugin_metadata_name",
        state=name)


async def delete_plugin(plugin_id: str):
    """
    Deletes FlowActionPlugin object.
    """
    return await dagor_delete_plugin(plugin_id)


async def get_plugins_list(flow_type: Optional[str], query: Optional[str]) -> dict:
    """
    Returns a list of available plugins.
    """

    plugins = await list_plugins(flow_type, query)

    groups = defaultdict(list)
    for plugin in plugins:
        if isinstance(plugin.plugin.metadata.group, list):
            for group in plugin.plugin.metadata.group:
                groups[group].append(plugin)
        elif isinstance(plugin.plugin.metadata.group, str):
            groups[plugin.plugin.metadata.group].append(plugin)

    # Sort
    groups = {k: sorted(v, key=lambda r: r.plugin.metadata.name, reverse=False) for k, v in groups.items()}

    return {
        "total": len(plugins),
        "grouped": groups
    }


async def install_plugins():
    return await install_default_plugins()
