from typing import List, Dict, Any
from collections import defaultdict

def flatten_taxonomy(taxonomy: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Index nodes by id
    nodes = {node["id"]: node for node in taxonomy}

    # Build parent → children map
    children_map = defaultdict(list)
    for node in taxonomy:
        parent_id = node["parent_id"]
        if parent_id is not None:
            children_map[parent_id].append(node["id"])

    results = []

    def traverse(node_id: str, path: List[str]):
        node = nodes[node_id]
        current_path = path + [node_id]

        examples = node.get("examples", {})

        if examples:
            # Each example gets a separate entry
            for example_name, values in examples.items():
                results.append({
                    "path": " > ".join(current_path),   # category path only
                    "entity": example_name,             # separate entity
                    "definition": node["definition"],
                    "examples": values
                })
        else:
            # Node without examples
            results.append({
                "path": " > ".join(current_path),
                "entity": None,  # no specific entity
                "definition": node["definition"],
                "examples": []
            })

        # Recurse into children
        for child_id in children_map.get(node_id, []):
            traverse(child_id, current_path)

    # Start from root nodes
    roots = [node["id"] for node in taxonomy if node["parent_id"] is None]
    for root_id in roots:
        traverse(root_id, [])

    return results