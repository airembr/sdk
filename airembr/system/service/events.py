import glob
import json
import os
from typing import Optional, Set, List

from durable_dot_dict.dotdict import DotDict

from airembr.model.system.context import get_context, ServerContext
from airembr.system.process.logging.log_handler import get_logger
from airembr.system.adapter.bigdata.big_data_adapter import *
from airembr.core.text.string_manager import capitalize_event_type_id

_local_dir = os.path.dirname(__file__)
_predefined_event_types = {}

logger = get_logger(__name__)


def _cache_predefined_event_types():
    if not _predefined_event_types:
        path = os.path.join(f"{_local_dir}/setup/events/*.json")
        for file_path in glob.glob(path):
            with open(file_path, "r") as file:
                try:
                    content = json.load(file)
                    for item in content:

                        try:
                            entity_name = item['entity_name']
                        except KeyError:
                            raise ValueError(f"Wrong configuration of `{file_path}`. Could not find `entity_name` key in {item}.")

                        try:
                            event_type = item['id']
                        except KeyError:
                            raise ValueError(f"Wrong configuration of `{file_path}`. Could not find `id` key in {item}.")

                        # (event_type, entity_name) = mapping
                        _predefined_event_types[(event_type, entity_name)] = item
                except Exception as e:
                    raise ValueError(f"Could not decode JSON for file {file_path}. Error: {repr(e)}")

def get_predefined_event_types():
    _cache_predefined_event_types()

    return _predefined_event_types.items()


def get_event_type_names():
    for _, event_def in get_predefined_event_types():
        yield event_def['id'], event_def['name']


async def get_event_types(limit: int = 1000, entity_type:str=None) -> dict:

    # No predefined events
    # pre_defined = list(get_event_type_names())
    # pre_defined_ids = [item[0] for item in pre_defined]

    pre_defined = []
    pre_defined_ids = []

    context = get_context()

    with ServerContext(context.switch_context(production=True)):
        for item in await bd_event_adapter.load_unique_event_types(limit, entity_type):
            if item not in pre_defined_ids:
                pre_defined.append((item, capitalize_event_type_id(item)))
                pre_defined_ids.append(item)

    with ServerContext(context.switch_context(production=False)):
        for item in await bd_event_adapter.load_unique_event_types(limit, entity_type):
            if item not in pre_defined_ids:
                pre_defined.append((item, capitalize_event_type_id(item)))

    events_types = [{"id": item[0], "name": item[1]} for item in sorted(pre_defined)]
    return {
        "total": len(events_types),
        "result": events_types
    }


async def get_event_actors(limit: int = 1000, entity_type:str=None) -> dict:

    # No predefined events
    # pre_defined = list(get_event_type_names())
    # pre_defined_ids = [item[0] for item in pre_defined]

    pre_defined = []
    pre_defined_ids = []

    context = get_context()

    with ServerContext(context.switch_context(production=True)):
        for item in await bd_event_adapter.load_unique_event_actor_types(limit, entity_type):
            if item not in pre_defined_ids:
                pre_defined.append((item, capitalize_event_type_id(item)))
                pre_defined_ids.append(item)

    with ServerContext(context.switch_context(production=False)):
        for item in await bd_event_adapter.load_unique_event_actor_types(limit, entity_type):
            if item not in pre_defined_ids:
                pre_defined.append((item, capitalize_event_type_id(item)))

    events_types = [{"id": item[0], "name": item[1]} for item in sorted(pre_defined)]
    return {
        "total": len(events_types),
        "result": events_types
    }

async def _get_keys(event_type, skip_type: List[str]=None):
    for _type, traits in await bd_event_adapter.load_events_by_type(event_type, limit=1000):
        if skip_type is not None and _type in skip_type:
            continue
        try:
            data = json.loads(traits)
            data = DotDict(data)
            data = data.flat()
            for key, value in data.items():
                if _type != 'rel':
                    yield f"entity.traits.{key}"
                else:
                    yield f"traits.{key}"
        except Exception as e:
            logger.error(repr(e))

async def get_event_traits_by_type(event_type:str, skip_type: List[str]=None) -> Set[str]:

    context = get_context()
    traits_keys = set()

    with ServerContext(context.switch_context(production=True)):
        async for item in _get_keys(event_type, skip_type):
            traits_keys.add(item)

    with ServerContext(context.switch_context(production=False)):
        async for item in _get_keys(event_type, skip_type):
            traits_keys.add(item)
    return traits_keys

def get_default_mappings_for(event_type, type) -> Optional[dict]:
    if not _predefined_event_types:
        _cache_predefined_event_types()

    schema = _predefined_event_types.get(event_type, None)

    if schema is None:
        return None

    return schema.get(type, None)


def get_default_event_type_schema(event_type, entity_name) -> Optional[dict]:
    if event_type not in _predefined_event_types:
        _cache_predefined_event_types()

    schema = _predefined_event_types.get((event_type, entity_name), None)
    return schema


def _append_value(values, value):
    if not isinstance(values, list):
        return [values]

    # Append list
    if isinstance(value, list):
        # Do this not to mutate
        _values = values + value
        # make it unique
        return list(set(_values))

    if isinstance(value, set):
        # Do this not to mutate
        _values = values + list(value)
        # make it unique
        return list(set(_values))

    # Append Value
    if value not in values:
        # Do this not to mutate
        _values = values + [value]
        return list(set(_values))

    return values

