import hashlib


def generate_pk(entity_type, entity_id) -> str:
    return hashlib.md5(f"{entity_type.lower()}-{entity_id}".encode()).hexdigest()

def generate_triplet_id(actor_pk, rel_label, object_pk) -> str:
    return hashlib.md5(f"{actor_pk}-{rel_label}-{object_pk}".encode()).hexdigest()