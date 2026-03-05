import json
import os
import numpy as np


def load_taxonomy(path="taxonomy.json"):
    """
    Load a taxonomy JSON file and convert all vector fields to NumPy arrays.
    Empty or missing vectors are converted to None.
    """
    with open(path, "r", encoding="utf-8") as f:
        taxonomy = json.load(f)

    def convert_vectors_category(category):
        # Convert category-level vectors
        for key in ["vector", "centroid_vector", "prototype_vector"]:
            v = category.get(key)
            category[key] = np.array(v) if v is not None else None

        # Convert entity-level vectors
        for entity_name, entity_data in category.get("entities", {}).items():
            for key in ["vector", "centroid_vector"]:
                v = entity_data.get(key)
                entity_data[key] = np.array(v) if v is not None else None

        return category

    taxonomy = [convert_vectors_category(cat) for cat in taxonomy]

    return taxonomy


taxonomy = load_taxonomy(os.path.join(os.path.dirname(__file__), "taxonomy.json"))
