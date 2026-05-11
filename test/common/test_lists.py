from airembr.core.list.spliter import split_list

def test_split_list():
    assert split_list("a,b,c") == ["a", "b", "c"]
    assert split_list(["a", "b"]) == ["a", "b"]
    assert split_list("") == []
    assert split_list(None) == []
    assert split_list(123) == []
