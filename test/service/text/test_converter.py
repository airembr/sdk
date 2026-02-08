from airembr.sdk.service.text.converter import to_camel_case

def test_to_camel_case_simple():
    assert to_camel_case("hello world") == "HelloWorld"

def test_to_camel_case_delimiters():
    assert to_camel_case("hello+world-this_is_a_test") == "HelloWorldThisIsATest"

def test_to_camel_case_empty():
    assert to_camel_case("") == ""

def test_to_camel_case_already_camel():
    # current implementation: HelloWorld -> Helloworld (it capitalizes EACH part)
    # Actually "HelloWorld" split is ["HelloWorld"], capitalize makes it "Helloworld"
    assert to_camel_case("HelloWorld") == "Helloworld"

def test_to_camel_case_multiple_spaces():
    assert to_camel_case("hello   world") == "HelloWorld"
