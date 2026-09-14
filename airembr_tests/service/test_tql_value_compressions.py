from airembr.sdk.service.parser.tql.utils.value_compressions import Values
from airembr.sdk.service.parser.tql.domain.operations import OrOperation, AndOperation

def test_values_init():
    v = Values()
    assert v.values == []

def test_append_or_value_simple():
    v = Values()
    v.append_or_value(1)
    assert v.values == [1]

def test_append_or_value_operation():
    v = Values()
    or_op = OrOperation({'bool': {'should': [1, 2, 3]}})
    v.append_or_value(or_op)
    assert v.values == [1, 2, 3]

def test_append_and_value_simple():
    v = Values()
    v.append_and_value(1)
    assert v.values == [1]

def test_append_and_value_operation():
    v = Values()
    and_op = AndOperation({'bool': {'must': [4, 5]}})
    v.append_and_value(and_op)
    assert v.values == [4, 5]

def test_mixed_appends():
    v = Values()
    v.append_or_value(1)
    v.append_and_value(AndOperation({'bool': {'must': [2, 3]}}))
    v.append_or_value(OrOperation({'bool': {'should': [4]}}))
    assert v.values == [1, 2, 3, 4]
