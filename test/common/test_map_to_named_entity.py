from unittest.mock import MagicMock
from airembr.sdk.common.map_to_named_entity import map_to_named_entity
from airembr.sdk.model.named_entity import NamedEntity

def test_map_to_named_entity():
    mock_table = MagicMock()
    mock_table.id = "ID123"
    mock_table.name = "Name123"
    
    result = map_to_named_entity(mock_table)
    assert isinstance(result, NamedEntity)
    assert result.id == "id123" # NamedEntity lowers the ID
    assert result.name == "Name123"
