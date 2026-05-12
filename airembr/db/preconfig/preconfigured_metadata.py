from typing import Optional, TypeVar, List, Callable, Dict

import os
from airembr.core.file.file_loaders import pre_config_file_loader

T = TypeVar("T")


class JsonWrapper:

    def __init__(self, data):
        self.data = data

    def get_by_id(self, id: str, cast: T = None) -> Optional[T]:

        if not self.data:
            return None

        data = self.data.get(id, None)

        if not data:
            return None

        if cast:
            return cast(**data)

        return data

    def values(self):
        return self.data.values()

    def keys(self):
        return self.data.keys()

    def items(self):
        return self.data.itemts()

    def __contains__(self, item) -> bool:
        return self.data and item in self.data

    def __len__(self) -> int:
        if not self.data:
            return 0
        return len(self.data)

    def empty(self) -> bool:
        return bool(self.data)

    def list_as(self, cast: T) -> List[T]:
        if not self.data:
            return []
        return [cast(**item) for item in self.data.values()]

    def filter(self, callable: Callable, cast: T = None) -> Dict[str, T]:

        if not self.data:
            return {}

        if cast:
            return {key: cast(**item) for key, item in self.data.items() if callable(item)}
        return {key: item for key, item in self.data.items() if callable(item)}

    def filter_as_list(self, callable: Callable, cast: T = None) -> List[T]:
        if not self.data:
            return []

        if cast:
            return [cast(**item) for item in self.data.values() if callable(item)]
        return [item for item in self.data.values() if callable(item)]


current_script_path = os.path.abspath(__file__)
current_script_directory = os.path.dirname(current_script_path)

# Metadata form files

pc_destinations = JsonWrapper(pre_config_file_loader(os.path.join(current_script_directory, 'data/destinations.json')))
pc_resources = JsonWrapper(pre_config_file_loader(os.path.join(current_script_directory, 'data/resources.json')))
pc_event_sources = JsonWrapper(pre_config_file_loader(os.path.join(current_script_directory, 'data/event-sources.json')))
pc_event_validation = JsonWrapper(pre_config_file_loader(os.path.join(current_script_directory, 'data/event-validations.json')))
pc_event_mapping = JsonWrapper(pre_config_file_loader(os.path.join(current_script_directory, 'data/event-mappings.json')))
pc_event_reshaping = JsonWrapper(pre_config_file_loader(os.path.join(current_script_directory, 'data/event-reshapings.json')))
pc_event_to_profile_mapping = JsonWrapper(pre_config_file_loader(os.path.join(current_script_directory, 'data/event-to-profile-mappings.json')))
pc_identification_points = JsonWrapper(pre_config_file_loader(os.path.join(current_script_directory, 'data/identification-points.json')))
