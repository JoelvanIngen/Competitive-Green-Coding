"""
IMPORTANT: FOR THIS MODULE TO WORK PLEASE CHANGE THE CONFIG.PY FILES IN BOTH THE DB AND SERVER TO
A 'REAL' HOST AND UNIQUE PORT NUMBERS SUCH THAT YOU CAN FIRST LOCALLY LAUNCH THESE SERVICES BEFORE
RUNNING THIS FILE!
"""

import asyncio
import random

import httpx
import pytest

from server.config import settings

NAMES = ["aap", "noot", "mies", "wim", "zus", "jet", "teun", "vuur", "gijs", "lam", "kees", "bok",
         "weide", "does", "hok", "duif", "schapen"]

URL = f"http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/api"


async def _get_request(*args, **kwargs):
    async with httpx.AsyncClient() as client:
        # Don't try/except in pytests, catch using pytest properties if necessary
        return await client.get(*args, **kwargs)


async def _post_request(*args, **kwargs):
    async with httpx.AsyncClient() as client:
        # Don't try/except in pytests, catch using pytest properties if necessary
        return await client.post(*args, **kwargs)


@pytest.mark.asyncio
async def try_register(data):
    response = await _post_request(f'{URL}/auth/register', json=data)
    if response.status_code == 200:
        token = response.json()
        print(token)
        return None, None
    elif response.status_code == 400:
        return response.headers["type"], response.headers["description"]


@pytest.mark.asyncio
async def test_username_in_use():
    username = random.choice(NAMES) + str(random.randint(0, 99))
    password = "password1234"

    data = {
        "username": username,
        "email": f"{username}@hotmail.com",
        "password": password
    }

    await try_register(data)

    data["email"] = "different_email@hotmail.com"

    type, description = await try_register(data)
    assert type == "username"
    assert description == "Username already in use"


@pytest.mark.asyncio
async def test_email_in_use():
    username = random.choice(NAMES) + str(random.randint(0, 99))
    password = "password1234"

    data = {
        "username": username,
        "email": f"{username}@hotmail.com",
        "password": password
    }

    await try_register(data)

    data["username"] = random.choice(NAMES) + str(random.randint(0, 99))

    type, description = await try_register(data)
    assert type == "email"
    assert description == "There already exists an account associated to this email"


@pytest.mark.asyncio
async def test_username_validation_error():
    username = random.choice(NAMES) + str(random.randint(0, 99)).zfill(32)
    password = "password1234"

    data = {
        "username": username,
        "email": f"{username}@hotmail.com",
        "password": password
    }

    type, description = await try_register(data)

    assert type == "username"
    assert description == "Username does not match constraints"

    data["username"] = random.choice(NAMES) + str(random.randint(0, 99)) + "!"

    type, description = await try_register(data)

    assert type == "username"
    assert description == "Username does not match constraints"


@pytest.mark.asyncio
async def test_email_validation_error():
    username = random.choice(NAMES) + str(random.randint(0, 99))
    password = "password1234"

    data = {
        "username": username,
        "email": "not_an_email",
        "password": password
    }

    type, description = await try_register(data)

    assert type == "email"
    assert description == "Invalid email format"


async def main():
    await test_username_in_use()
    await test_email_in_use()
    await test_username_validation_error()
    await test_email_validation_error()


if __name__ == "__main__":
    asyncio.run(main())
