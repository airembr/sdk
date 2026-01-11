import hashlib


def generate_pk(entity_type, entity_id) -> str:
    return hashlib.md5(f"{entity_type}-{entity_id}".encode()).hexdigest()