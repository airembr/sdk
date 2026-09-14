from airembr.sdk.service.parser.tql.utils.dictonary import flatten

def test_flatten_empty():
    assert flatten({}) == {}

def test_flatten_simple():
    d = {"a": 1, "b": 2}
    expected = {"a": 1, "b": 2}
    # Note: flatten mutates the dictionary, so we pass a copy if we want to keep d
    assert flatten(d.copy()) == expected

def test_flatten_nested():
    d = {"a": {"b": 1}, "c": 2}
    expected = {"a.b": 1, "c": 2}
    assert flatten(d.copy()) == expected

def test_flatten_deeply_nested():
    d = {"a": {"b": {"c": 3}}, "d": 4}
    expected = {"a.b.c": 3, "d": 4}
    assert flatten(d.copy()) == expected

def test_flatten_multiple_keys_in_nested():
    d = {"a": {"b": 1, "c": 2}, "d": 3}
    expected = {"a.b": 1, "a.c": 2, "d": 3}
    assert flatten(d.copy()) == expected

def test_flatten_mutation_side_effect():
    d = {"a": {"b": 1}}
    flatten(d)
    assert d == {} # The original implementation does d.popitem() until empty and returns a new dict
