from typing import Union
from durable_dot_dict.dotdict import DotDict


def _key_value_to_string(key, value):
    if isinstance(value, (dict, list)):
        return f"{key}={value}"
    elif isinstance(value, (int, float, bool)):
        return f"{key}={value}"
    else:
        return f'{key}="{value}"'


def format_traits(traits: Union[DotDict, dict]) -> str:
    if isinstance(traits, dict):
        traits = DotDict(traits)
    flat = traits.flat()
    properties = [_key_value_to_string(key, value) for key, value in flat.items()]
    return f"({', '.join(properties)})"
