from airembr.model.metadata.sys_evt_validation import EventValidator
from airembr.system.adapter.metadata.mysql.interface import event_validation_dao
from airembr.system.command.v1.errors.validator_errors import EventValidationError


async def add_validator(data: EventValidator):
    await event_validation_dao.insert(data)


async def delete_validator(validator_id: str):
    return await event_validation_dao.delete_by_id(validator_id)


async def get_validator(validator_id: str) -> EventValidator:
    validator = await event_validation_dao.load_by_id(validator_id)
    if not validator:
        raise EventValidationError(f"No event validation with ID {validator_id} found.", 404)
    return validator
