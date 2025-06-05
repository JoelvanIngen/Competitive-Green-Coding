import os
import subprocess
import random
import string
import requests

N_USERS = 10
N_PROBLEMS = 5
N_SUBMISSIONS = 20
NAMES = ["aap", "noot", "mies", "wim", "zus", "jet", "teun", "vuur", "gijs", "lam", "kees", "bok",
         "weide", "does", "hok", "duif", "schapen"]

DB_PATH = "db/src/db/db_handler.py"


def reset_and_launch_db():
    """Remove database if present and fastapi server.
    """
    if "database.db" in os.listdir():
        os.remove("database.db")

    subprocess.Popen(['fastapi', 'dev', DB_PATH])


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

        entry = requests.post('http://127.0.0.1:8000/users/', json=data).json()

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

        entry = requests.post('http://127.0.0.1:8000/problems/', json=data).json()

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
        requests.post('http://127.0.0.1:8000/submissions/', json=data)


if __name__ == "__main__":
    reset_and_launch_db()
    while "database.db" not in os.listdir():
        pass
    uuids = populate_users(N_USERS)
    pids = populate_problems(N_PROBLEMS)
    populate_submissions(N_SUBMISSIONS, uuids, pids)
