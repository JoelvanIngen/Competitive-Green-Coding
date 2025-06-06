import random

import httpx
import pytest

from .config import HOST, PORT

pytest_plugins = ('pytest_asyncio',)

URL = f"http://{HOST}:{PORT}/api"

N_USERS = 10
N_PROBLEMS = 5
N_SUBMISSIONS = 20
NAMES = ["aap", "noot", "mies", "wim", "zus", "jet", "teun", "vuur", "gijs", "lam", "kees", "bok",
         "weide", "does", "hok", "duif", "schapen"]


async def _get_request(*args, **kwargs):
    with httpx.AsyncClient() as client:
        # Don't try/except in pytests, catch using pytest properties if necessary
        return client.post(*args, **kwargs)


async def _post_request(*args, **kwargs):
    with httpx.AsyncClient() as client:
        # Don't try/except in pytests, catch using pytest properties if necessary
        return client.post(*args, **kwargs)


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
            "password": password
        }

        entry = (await _post_request(f'{URL}/auth/register/', json=data)).json()
        print(entry)

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
  

def find_me(token: dict[str, str]):
    entry = requests.get(f'{URL}/users/me/', json=token).json()

    return entry

  
# def populate_problems(N_problems: int) -> list[int]:
#     """Populate db with problems with incremented problem ids and randomly generated tags, and
#     names.

#     Args:
#         N_problems (int): number of problems to populate db with

#     Returns:
#         list[int]: generated problem ids
#     """
#     pids = []

#     for _ in range(N_problems):
#         name = f"{random.choice(NAMES)} problem #{random.randint(1, 10)}"
#         tags = [random.choice(['C', 'python'])]

#         data = {
#             "name": name,
#             "tags": tags,
#             "description": "test description"
#         }

#         entry = requests.post(f'{URL}/problems/', json=data).json()

#         pids.append(entry["problem_id"])

#     return pids


# def populate_submissions(N_submissions: int, uuids: list[str], pids: list[int]):
#     """Populate db with submissions with randomly generated ids, tags, and names.

#     Args:
#         N_problems (int): number of problems to populate db with
#         uuids (list[UUID]): used user ids
#         pids (list[int]): used process ids
#     """

#     data = {
#         "problem_id": pids[0],
#         "uuid": uuids[0],
#         "timestamp": 0,
#         "code": "string"
#     }

#     for _ in range(N_SUBMISSIONS):
#         requests.post(f'{URL}/submissions/', json=data)


if __name__ == "__main__":
    usernames = populate_users(N_USERS)
    token = try_password(usernames[0], 'password1234')
    print(token)
    print(find_me(token))
    try_password('kees3', 'password12345')

    # pids = populate_problems(N_PROBLEMS)
    # populate_submissions(N_SUBMISSIONS, uuids, pids)
