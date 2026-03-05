import json

from sentence_transformers import SentenceTransformer
import numpy as np

from airembr.sdk.ai.taxonomy.entity_taxonomy import taxonomy


def save_taxonomy(taxonomy, path="taxonomy.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            taxonomy,
            f,
            ensure_ascii=False,
            indent=2
        )


def create_embeddings(taxonomy, negative_strength=0.3):
    model = SentenceTransformer("intfloat/multilingual-e5-small")

    def embed(texts):
        if isinstance(texts, str):
            texts = [texts]
        texts = [f"passage: {t}" for t in texts]
        return model.encode(texts, normalize_embeddings=True)

    def safe_centroid(vectors):
        """Compute centroid of a list of vectors safely. Returns None if empty."""
        if not vectors:
            return None
        return np.mean(np.array(vectors), axis=0)

    # ---- compute entity + category centroids ----
    for category in taxonomy:

        definition = category.get("definition", "")

        definition_text = f"{definition}. "
        entities = category.get("entities", {})
        if entities:
            definition_text += f"Entity examples: {', '.join(entities.keys())}"

        category["vector"] = embed(definition_text)[0].tolist()

        entity_centroids = []

        for entity_name, entity_data in entities.items():

            examples = entity_data.get("examples", [])
            entity_definition = entity_data.get("definition", definition)

            entity_text = f"Text mentions entity: {entity_name}: {entity_definition}\nExamples: {', '.join(examples)}"
            print(entity_text)
            entity_vec = embed(entity_text)[0]
            entity_data["vector"] = entity_vec.tolist()

            # embed examples (skip empty)
            example_vecs = embed(examples) if examples else []

            entity_centroid = safe_centroid(list(example_vecs) + [entity_vec])
            if entity_centroid is not None:
                entity_data["centroid_vector"] = entity_centroid.tolist()
                entity_centroids.append(entity_centroid)

        category_centroid = safe_centroid(entity_centroids)
        if category_centroid is not None:
            category["centroid_vector"] = category_centroid.tolist()
        else:
            category["centroid_vector"] = None  # no entities

    # ---- compute prototype vectors with negative centroids ----
    category_centroids = [
        np.array(c["centroid_vector"])
        for c in taxonomy
        if c.get("centroid_vector") is not None
    ]

    for i, category in enumerate(taxonomy):
        if category.get("centroid_vector") is None:
            category["prototype_vector"] = None
            continue

        positive = np.array(category["centroid_vector"])

        # negative centroids exclude self
        negatives = [
            c for j, c in enumerate(category_centroids)
            if j != i
        ]

        if negatives:
            negative_centroid = safe_centroid(negatives)
            prototype = positive - negative_strength * negative_centroid
        else:
            prototype = positive

        # normalize
        norm = np.linalg.norm(prototype)
        if norm > 0:
            prototype /= norm

        category["prototype_vector"] = prototype.tolist()

    return taxonomy


x = create_embeddings(taxonomy)
save_taxonomy(x)
