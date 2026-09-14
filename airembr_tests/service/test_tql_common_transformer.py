import pytest
from airembr.sdk.service.parser.tql.transformer.common_transformer import CommonTransformer
from unittest.mock import MagicMock

@pytest.fixture
def transformer():
    return CommonTransformer()

def test_escaped_string(transformer):
    mock_arg = MagicMock()
    mock_arg.value = '"hello"'
    assert transformer.ESCAPED_STRING(mock_arg) == ('ESCAPED_STRING', 'hello')

def test_integer(transformer):
    mock_arg = MagicMock()
    mock_arg.value = '123'
    assert transformer.INTEGER(mock_arg) == ('INTEGER', '123')

def test_bool(transformer):
    mock_arg = MagicMock()
    mock_arg.value = 'True'
    assert transformer.BOOL(mock_arg) == ('BOOL', True)
    mock_arg.value = 'false'
    assert transformer.BOOL(mock_arg) == ('BOOL', False)

def test_float(transformer):
    mock_arg = MagicMock()
    mock_arg.value = '1.23'
    assert transformer.FLOAT(mock_arg) == ('FLOAT', '1.23')

def test_value_escaped_string(transformer):
    mock_arg = MagicMock()
    mock_arg.type = 'ESCAPED_STRING'
    mock_arg.value = '"hello"'
    assert transformer.value([mock_arg]) == ('ESCAPED_STRING', 'hello')

def test_value_other_type(transformer):
    mock_arg = MagicMock()
    mock_arg.type = 'SOME_TYPE'
    mock_arg.value = 'some_value'
    assert transformer.value([mock_arg]) == ('SOME_TYPE', 'some_value')

def test_value_with_namespace(transformer):
    mock_arg = MagicMock()
    mock_arg.type = 'namespace__TYPE'
    mock_arg.value = 'val'
    assert transformer.value([mock_arg]) == ('TYPE', 'val')

def test_compound_value_date(transformer):
    result = transformer.compound_value(['date', ('STRING', '2023-01-01')])
    assert result == ('date', '2023-01-01T00:00:00Z')

def test_compound_value_invalid_date(transformer):
    with pytest.raises(ValueError) as excinfo:
        transformer.compound_value(['date', ('STRING', 'not-a-date')])
    assert "Could not parse date" in str(excinfo.value)

def test_compound_value_unknown_type(transformer):
    with pytest.raises(ValueError) as excinfo:
        transformer.compound_value(['unknown', ('STRING', 'val')])
    assert "Unknown parse function" in str(excinfo.value)
