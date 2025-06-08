import random

import httpx
import pytest
import asyncio

from config import HOST, PORT

pytest_plugins = ('pytest_asyncio',)

URL = f"http://{HOST}:{PORT}/api"

N_USERS = 1
N_PROBLEMS = 5
N_SUBMISSIONS = 20
NAMES = ["aap", "noot", "mies", "wim", "zus", "jet", "teun", "vuur", "gijs", "lam", "kees", "bok",
         "weide", "does", "hok", "duif", "schapen"]


async def _get_request(*args, **kwargs):
    async with httpx.AsyncClient() as client:
        # Don't try/except in pytests, catch using pytest properties if necessary
        return await client.get(*args, **kwargs)


async def _post_request(*args, **kwargs):
    async with httpx.AsyncClient() as client:
        # Don't try/except in pytests, catch using pytest properties if necessary
        return await client.post(*args, **kwargs)


@pytest.mark.asyncio
async def test_populate_users(n_users: int) -> list[str]:
    """Populate db with users with randomly generated ids, usernames and hashed passwords.

    Args:
        n_users (int): number of users to populate db with

    Returns:
        list[int]: generated usernames
    """
    _usernames = []

    for _ in range(n_users):
        username = random.choice(NAMES) + str(random.randint(0, 9))
        password = "password1234"

        data = {
            "username": username,
            "email": f"{username}@hotmail.com",
            "password": password,
            "permission_level": "user"
        }

        entry = await _post_request(f'{URL}/auth/register/', json=data)
        entry = entry.json()

        try:
            _usernames.append(entry["username"])
        except Exception:
            print(entry['detail'])

    return _usernames


@pytest.mark.asyncio
async def try_password(username: str, password: str) -> dict[str, str]:
    data = {
        "username": username,
        "password": password
    }

    token = (await _post_request(f'{URL}/auth/login/', json=data)).json()
    return token


@pytest.mark.asyncio
async def find_me(token: dict[str, str]):
    entry = (await _post_request(f'{URL}/users/me/', json=token)).json()

    return entry


async def main():
    usernames = await test_populate_users(N_USERS)
    token = await try_password(usernames[0], 'password1234')
    print(token)
    print(await find_me(token))
    await try_password(usernames[0], 'password12345')


if __name__ == "__main__":
    asyncio.run(main())
