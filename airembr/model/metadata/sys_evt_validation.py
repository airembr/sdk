import jsonschema
from typing import Optional, List, Any
from pydantic import field_validator, BaseModel

from airembr.model.system.named_entity import NamedEntityInContext
from airembr.sdk.service.parser.tql.condition import Condition


class ValidationSchema(BaseModel):
    json_schema: dict
    condition: Optional[str] = None

    @field_validator("json_schema")
    @classmethod
    def validate_schemas_format(cls, v):
        for value in v.values():
            try:
                jsonschema.Draft202012Validator.check_schema(value)
            except jsonschema.SchemaError as e:
                raise ValueError(f"Validation JSON-schema is invalid. Please refer to documentation "
                                 f"for the JSON-schema format. "
                                 f"Error message: {str(e)}")
        return v

    @field_validator("condition")
    @classmethod
    def check_if_condition_valid(cls, value):
        if value:
            try:
                condition = Condition()
                condition.parse(value)
            except Exception as _:
                raise ValueError("Given condition expression is invalid.")
            return value
        else:
            return None


class EventValidator(NamedEntityInContext):
    event_type: str
    entity_type: str
    description: Optional[str] = "No description provided"
    tags: List[str] = []
    validation: ValidationSchema
    ttl: Optional[int] = -1
    enabled: bool = False
    locked: Optional[bool] = False

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.event_type = self.event_type.lower()
        self.entity_type = self.entity_type.lower()