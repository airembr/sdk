import asyncio
from uuid import uuid4

import pytest

from airembr.model.system.context import Context, ServerContext
from airembr.model.metadata.sys_user import User
from airembr.model.metadata.user_payload import UserPayload
from airembr.system.command.v1.errors.user_errors import UserError
from airembr.system.command.v1.meta.user.add_user import add_user
from airembr.system.command.v1.meta.user.get_user import get_user
from airembr.system.command.v1.meta.user.edit_user import edit_user
from airembr.system.command.v1.meta.user.delete_user import delete_user


def _make_payload(email: str, roles=None) -> UserPayload:
    return UserPayload(password="Sup3rSecret!", name="Test User", email=email, roles=roles or ["user"], enabled=True)


def _other_requesting_user() -> User:
    return User(id=f"requester-{uuid4()}", password="x", name="Requester", email="requester@example.com", roles=["admin"])


def test_crud_user_create_and_read():
    with ServerContext(Context()):
        async def scenario():
            email = f"test-user-{uuid4()}@example.com"
            user_id = await add_user(_make_payload(email))

            fetched = await get_user(user_id)

            assert fetched is not None
            assert fetched.id == user_id
            assert fetched.email == email
            assert fetched.password is None
        asyncio.run(scenario())


def test_crud_user_update():
    with ServerContext(Context()):
        async def scenario():
            email = f"test-user-{uuid4()}@example.com"
            user_id = await add_user(_make_payload(email))
            requesting_user = _other_requesting_user()

            updated_payload = _make_payload(email, roles=["user", "editor"])
            saved, updated_user = await edit_user(user_id, updated_payload, requesting_user)

            assert saved is True
            assert "editor" in updated_user.roles
        asyncio.run(scenario())


def test_crud_user_delete():
    with ServerContext(Context()):
        async def scenario():
            email = f"test-user-{uuid4()}@example.com"
            user_id = await add_user(_make_payload(email))
            requesting_user = _other_requesting_user()

            await delete_user(user_id, requesting_user)

            with pytest.raises(UserError) as exc_info:
                await get_user(user_id)
            assert exc_info.value.status_code == 404
        asyncio.run(scenario())


def test_add_user_duplicate_email_raises_409():
    with ServerContext(Context()):
        async def scenario():
            email = f"test-user-{uuid4()}@example.com"
            await add_user(_make_payload(email))

            with pytest.raises(UserError) as exc_info:
                await add_user(_make_payload(email))
            assert exc_info.value.status_code == 409
        asyncio.run(scenario())


def test_get_user_missing_raises_404():
    with ServerContext(Context()):
        async def scenario():
            with pytest.raises(UserError) as exc_info:
                await get_user(f"test-user-{uuid4()}")
            assert exc_info.value.status_code == 404
        asyncio.run(scenario())
