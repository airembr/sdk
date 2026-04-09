from typing import List, Dict, Any

def sort_dicts_by_id_order(
    data: List[Dict[str, Any]],
    ids: List[str],
    sort_key: str = "id",
    unknown_last: bool = True,
) -> List[Dict[str, Any]]:
    """
    Sort a list of dicts based on the order of IDs.

    :param data: List of dictionaries (each must contain id_key)
    :param ids: List defining the desired order
    :param sort_key: Key in dict that holds the ID
    :param unknown_last: If True, items with IDs not in `ids` go to the end
    :return: New sorted list
    """
    order_map = {id_: i for i, id_ in enumerate(ids)}

    if unknown_last:
        return sorted(data, key=lambda x: order_map.get(x.get(sort_key), float("inf")))
    else:
        return sorted(data, key=lambda x: order_map.get(x.get(sort_key), -1))