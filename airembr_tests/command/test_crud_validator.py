import asyncio
from uuid import uuid4

import pytest

from airembr.model.system.context import Context, ServerContext
from airembr.model.metadata.sys_evt_validation import EventValidator, ValidationSchema
from airembr.system.command.v1.errors.validator_errors import EventValidationError
from airembr.system.command.v1.meta.validator.validator import add_validator, get_validator, delete_validator


def _make_validator(validator_id: str) -> EventValidator:
    return EventValidator(
        id=validator_id,
        name="Test Validator",
        event_type="test-event",
        entity_type="person",
        validation=ValidationSchema(json_schema={}),
    )


def test_crud_validator_create_and_read():
    with ServerContext(Context()):
        async def scenario():
            validator_id = f"test-validator-{uuid4()}"
            await add_validator(_make_validator(validator_id))

            fetched = await get_validator(validator_id)

            assert fetched is not None
            assert fetched.id == validator_id
            assert fetched.name == "Test Validator"
        asyncio.run(scenario())


def test_crud_validator_delete():
    with ServerContext(Context()):
        async def scenario():
            validator_id = f"test-validator-{uuid4()}"
            await add_validator(_make_validator(validator_id))

            await delete_validator(validator_id)

            with pytest.raises(EventValidationError):
                await get_validator(validator_id)
        asyncio.run(scenario())


def test_crud_validator_get_missing_raises_404():
    with ServerContext(Context()):
        async def scenario():
            with pytest.raises(EventValidationError) as exc_info:
                await get_validator(f"test-validator-{uuid4()}")
            assert exc_info.value.status_code == 404
        asyncio.run(scenario())
