from durable_dot_dict.dotdict import DotDict


class FlatText(DotDict):
    ID = "id"
    PARENT_ID = "parent_id"
    TEXT = "text_string"
    TAGS = "tags"
    REQUIRE_NER = "require_ner"
    TS = "ts"

