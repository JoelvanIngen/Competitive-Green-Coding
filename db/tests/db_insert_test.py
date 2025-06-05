import random
import string
import requests

from config import HOST, PORT

URL = f"http://{HOST}:{PORT}/api"

N_USERS = 10
N_PROBLEMS = 5
N_SUBMISSIONS = 20
NAMES = ["aap", "noot", "mies", "wim", "zus", "jet", "teun", "vuur", "gijs", "lam", "kees", "bok",
         "weide", "does", "hok", "duif", "schapen"]


def populate_users(N_users: int) -> list[str]:
    """Populate db with users with randomly generated ids, usernames and hashed passwords.

    Args:
        N_users (int): number of users to populate db with

    Returns:
        list[int]: generated user ids
    """
    uuids = []

    for _ in range(N_users):
        username = random.choice(NAMES) + str(random.randint(0, 9))
        password = "".join(random.choices(string.ascii_letters, k=32))

        data = {
            "username": username,
            "email": f"{username}@hotmail.com",
            "password_hash": password
        }

        entry = requests.post(f'{URL}/users/', json=data).json()

        uuids.append(entry["uuid"])

    return uuids


def populate_problems(N_problems: int) -> list[int]:
    """Populate db with problems with incremented problem ids and randomly generated tags, and
    names.

    Args:
        N_problems (int): number of problems to populate db with

    Returns:
        list[int]: generated problem ids
    """
    pids = []

    for _ in range(N_problems):
        name = f"{random.choice(NAMES)} problem #{random.randint(1, 10)}"
        tags = [random.choice(['C', 'python'])]

        data = {
            "name": name,
            "tags": tags,
            "description": "test description"
        }

        entry = requests.post(f'{URL}/problems/', json=data).json()

        pids.append(entry["problem_id"])

    return pids


def populate_submissions(N_submissions: int, uuids: list[str], pids: list[int]):
    """Populate db with submissions with randomly generated ids, tags, and names.

    Args:
        N_problems (int): number of problems to populate db with
        uuids (list[UUID]): used user ids
        pids (list[int]): used process ids
    """

    data = {
        "problem_id": pids[0],
        "uuid": uuids[0],
        "timestamp": 0,
        "code": "string"
    }

    for _ in range(N_SUBMISSIONS):
        requests.post(f'{URL}/submissions/', json=data)


if __name__ == "__main__":
    uuids = populate_users(N_USERS)
    pids = populate_problems(N_PROBLEMS)
    populate_submissions(N_SUBMISSIONS, uuids, pids)
