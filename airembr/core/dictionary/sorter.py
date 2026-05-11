from typing import List, Dict, Any


def sort_dicts_by_id_order(data: List[Dict[str, Any]],
                           sort_by_ids: List[str],
                           sort_key: str = "id"):
    order_map = {id_: i for i, id_ in enumerate(sort_by_ids)}
    data.sort(key=lambda x: order_map.get(x.get(sort_key), float("inf")))

    return data