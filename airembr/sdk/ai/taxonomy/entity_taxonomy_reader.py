from time import time

import numpy as np
from sentence_transformers import SentenceTransformer

from airembr.sdk.ai.taxonomy.entity_taxonomy import taxonomy
from airembr.sdk.ai.taxonomy.text_chunker import get_text_semantic_chunker

# Load the same embedding model
model = SentenceTransformer("intfloat/multilingual-e5-small")

def get_entity_vectors(taxonomy, vectors = 'vector,prototype_vector,centroid_vector'):
    """
    Returns a list of (entity_name, category_id, vector) tuples for all entities in the taxonomy.
    Only includes entities with a valid vector (non-None).
    """
    entity_vectors = []
    vectors = vectors.split(',')
    for category in taxonomy:
        category_id = category.get("id")
        parent_id = category.get("parent_id")
        for entity_name, entity_data in category.get("entities", {}).items():
            for vec_name in vectors:
                vec = entity_data.get(vec_name, None)
                if vec is not None:
                    entity_vectors.append((entity_name, category_id, parent_id, vec))

    return entity_vectors


def get_category_vectors(taxonomy, vector_key='vector'):
    """
    Returns a list of (category_id, definition_vector) tuples for all categories in the taxonomy.
    Only includes categories with a valid vector (non-None).

    vector_key can be 'vector', 'centroid_vector', or 'prototype_vector'
    """
    category_vectors = []

    for category in taxonomy:
        category_id = category.get("id")
        parent_id = category.get("parent_id")
        vec = category.get(vector_key)
        if vec is not None:
            category_vectors.append((None, category_id, parent_id, vec))

    return category_vectors


def embed_text(text, type='passage'):
    """
    Embed a single text using the same model and normalize.
    """
    vec = model.encode(f"{type}: {text}", normalize_embeddings=True)
    return vec


def cosine_similarity(a, b):
    return np.dot(a, b)  # vectors already normalized


def categorize_text(text, entity_vectors, type, top_k=5):
    """
    text: string to match
    entity_vectors: list of (entity_name, category_id, vector)
    Returns top_k matches sorted by cosine similarity,
    including both cosine similarity and Euclidean distance.
    """
    text_vec = embed_text(text, type)

    results = []
    for entity_name, category_id, parent_id, vec in entity_vectors:
        if vec is not None:
            # cosine similarity (vectors assumed normalized)
            cos_sim = np.dot(text_vec, vec)
            # Euclidean distance
            euclid_dist = np.linalg.norm(text_vec - vec)
            results.append((cos_sim, euclid_dist, entity_name, category_id, parent_id))

    results.sort(reverse=True, key=lambda x: x[0])

    return results[:top_k]


def yield_entity_classes_per_chunk(text, type, taxonomy):
    # Load taxonomy and entity vectors
    entity_vectors = get_entity_vectors(taxonomy)

    chunker = get_text_semantic_chunker(2048)

    for chunk in chunker(text):
        if len(chunk) < 100:
            top_k =5
        else:
            top_k = 10

        # Categorize according to taxonomy
        top_matches = categorize_text(chunk, entity_vectors, type, top_k=top_k)
        categories = []
        category_list = []
        for score, l2, entity, category, parent in top_matches:
            categories.append((f"{parent}/{category}/{entity}", score))
            category_list.append(f"{parent}/{category}/{entity}")

        parent_categories = []
        category_vectors = get_category_vectors(taxonomy)
        top_matches = categorize_text(" ".join(category_list), category_vectors, type, top_k=3)
        for score, l2, entity, category, parent in top_matches:
            parent_categories.append((f"{parent}/{category}", score))

        yield chunk, parent_categories, categories


text = """
What did Calvin discuss with the cool artist he met at the gala?
"""
t = time()
for chunk, c, a in yield_entity_classes_per_chunk(text, 'query', taxonomy):
    print(f"Chunk: {chunk}")
    print(f"Categories: {c}")
    print(f"Entities: {a}")
print(time() - t)