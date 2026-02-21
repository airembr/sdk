import pytest
from airembr.sdk.common.getters import get_entity_id, get_entity, get_primary_entity
from airembr.sdk.model.entity import Entity, PrimaryEntity, FlatEntity

def test_get_entity_id_from_entity():
    entity = Entity(id="123")
    assert get_entity_id(entity) == "123"
    
    entity_no_id = Entity.construct() # Pydantic construct bypasses validation
    entity_no_id.id = None
    assert get_entity_id(entity_no_id, default="def") == "def"

def test_get_entity_id_from_flat_entity():
    flat_entity = FlatEntity({"hash": "456"})
    assert get_entity_id(flat_entity) == "456"
    
    flat_entity_no_id = FlatEntity({})
    assert get_entity_id(flat_entity_no_id, default="def") == "def"

def test_get_entity_id_from_dict():
    d = {"id": "789"}
    assert get_entity_id(d) == "789"
    
    d_no_id = {}
    assert get_entity_id(d_no_id, default="def") == "def"

def test_get_entity_id_invalid_type():
    with pytest.raises(ValueError):
        get_entity_id(123)

def test_get_entity():
    entity = Entity(id="123")
    result = get_entity(entity)
    assert isinstance(result, Entity)
    assert result.id == "123"
    
    flat_entity = FlatEntity({"hash": "456"})
    result = get_entity(flat_entity)
    assert isinstance(result, Entity)
    assert result.id == "456"
    
    assert get_entity(None) is None
    assert get_entity({"id": "123"}) is None # Only Entity or FlatEntity

def test_get_primary_entity():
    pe = PrimaryEntity(id="123", primary_id="p123")
    result = get_primary_entity(pe)
    assert isinstance(result, PrimaryEntity)
    assert result.id == "123"
    assert result.primary_id == "p123"
    
    assert get_primary_entity(None) is None
    assert get_primary_entity(Entity(id="123")) is None
