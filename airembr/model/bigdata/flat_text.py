from durable_dot_dict.dotdict import DotDict


class FlatText(DotDict):
    ID = "id"
    PARENT_ID = "parent_id"
    OBSERVATION_ID = "observation.id"
    TEXT = "text_string"
    TAGS = "tags"
    ORIGIN = "origin"
    REQUIRE_NER = "require_ner"
    CHUNKED = "chunked"
    MODEL = "model"
    TS = "ts"

