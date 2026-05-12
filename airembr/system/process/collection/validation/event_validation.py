import jsonschema
from typing import Tuple, Optional, List

from durable_dot_dict.dotdict import DotDict

from airembr.model.bigdata.flat_ent_history import FlatEntityHistory
from airembr.sdk.service.dot_accessor import DotAccessor
from airembr.model.process_status import ProcessStatus
from airembr.core.exception.exception import EventValidationException
from airembr.model.metadata.sys_evt_validation import EventValidator
from airembr.system.adapter.metadata.mysql.interface import event_validation_dao
from airembr.sdk.service.parser.tql.parser import Parser
from airembr.sdk.service.parser.tql.transformer.expr_transformer import ExprTransformer

parser = Parser(Parser.read('grammar/uql_expr.lark'), start='expr')


def _validate(validator: EventValidator, dot: DotAccessor) -> Tuple[bool, Optional[str]]:
    for key, val_schema in validator.validation.json_schema.items():
        if not DotAccessor.validate(key):
            raise EventValidationException(
                f"Please correct the reference to data in your validation schema. Expected dot notation got {key}")

        try:
            value = dot[key].to_dict() if isinstance(dot[key], DotDict) else dot[key]
            jsonschema.validate(value, val_schema)
        except jsonschema.ValidationError as e:
            return True, str(e)
        except KeyError as e:
            return True, str(e)

    return False, None


def _get_validators_that_meet_condition(validators, dot: DotAccessor):
    validators_to_use = []
    for validator in validators:
        if validator.validation.condition:
            try:
                condition = ExprTransformer(dot=dot).transform(
                    tree=parser.parse(validator.validation.condition))
            except Exception:
                condition = False
        else:
            condition = True

        if condition:
            validators_to_use.append(validator)

    return validators_to_use


async def _get_event_validation_result(flat_event_entity: DotDict, validation_schemas: List[EventValidator]) -> Tuple[
    bool, Optional[str]]:
    if validation_schemas:

        dot = DotAccessor(
            event=flat_event_entity,
            flow=None,
            memory=None
        )

        validators_to_use = _get_validators_that_meet_condition(validation_schemas, dot)

        for validator in validators_to_use:
            if validator.entity_type != flat_event_entity[FlatEntityHistory.ENTITY_TYPE]:
                # Skip validation that is not for current entity type
                return False, None
            error, message = _validate(validator, dot)
            if error:
                return error, message
        return False, None

    return False, None


async def validate_event(event_type: str, data: DotDict) -> ProcessStatus:
    validation_schemas: List[EventValidator] = await event_validation_dao.load_event_validation(event_type)

    # Validate events

    validation_error, error_message = await _get_event_validation_result(
        data,
        validation_schemas
    )

    return ProcessStatus(error=validation_error, message=error_message)
