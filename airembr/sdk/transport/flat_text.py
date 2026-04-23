from durable_dot_dict.dotdict import DotDict


class FlatText(DotDict):
    ID = "id"
    PARENT_ID = "parent_id"
    OBSERVATION_ID = "observation.id"
    SOURCE_ID = "source.id"
    REL_LABEL = "rel.label"
    REL_TYPE = "rel.type"
    DESCRIPTION = "description"
    TAGS = "tags"
    MODEL = "model"
    VECTOR = "vector"
    REQUIRE_NER = "require_ner"
    TS = "ts"

