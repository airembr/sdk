from durable_dot_dict.dotdict import DotDict


class FlatText(DotDict):
    ID = "id"
    PARENT_ID = "parent_id"
    OBSERVATION_ID = "observation.id"
    TEXT = "text_string"
    TAGS = "tags"
    # 1. Observation description
    # 2. Fact description
    # 3. Entity description
    # 4. Question to observation
    # 5. Question to fact
    ORIGIN = "origin"
    REQUIRE_NER = "require_ner"
    CHUNKED = "chunked"
    MODEL = "model"
    TS = "ts"

