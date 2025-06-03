import os
import subprocess
import random
import string
import requests

N_USERS = 10
N_PROBLEMS = 5
NAMES = ["aap", "noot", "mies", "wim", "zus", "jet", "teun", "vuur", "gijs", "lam", "kees", "bok",
         "weide", "does", "hok", "duif", "schapen"]

DB_PATH = "server/src/db/db_interface.py"


def reset_and_launch_db():
    """Remove database if present and fastapi server.
    """
    if "database.db" in os.listdir():
        os.remove("database.db")

    subprocess.Popen(['fastapi', 'dev', DB_PATH])


def populate_users(N_users: int):
    """Populate db with users with randomly generated ids, usernames and hashed passwords.

    Args:
        N_users (int): number of users to populate db with
    """
    for _ in range(N_users):
        uuid = random.randint(0, 10 ** 16)
        username = random.choice(NAMES) + str(random.randint(0, 9))
        password = "".join(random.choices(string.ascii_letters, k=32))

        data = {
            "uuid": uuid,
            "username": username,
            "email": f"{username}@hotmail.com",
            "password_hash": password
        }

        requests.post('http://127.0.0.1:8000/users/', json=data)


def populate_problems(N_problems: int):
    """Populate db with problems with randomly generated ids, tags, and names.

    Args:
        N_problems (int): number of problems to populate db with
    """
    for pid in range(N_problems):
        name = f"{random.choice(NAMES)} problem #{random.randint(1,10)}"
        tags = random.randbytes(4)

        data = {
            "problem_id": pid,
            "name": name,
            "tags": int.from_bytes(tags),
            "description": "test description"
        }

        requests.post('http://127.0.0.1:8000/problems/', json=data)


if __name__ == "__main__":
    reset_and_launch_db()
    while "database.db" not in os.listdir():
        pass
    populate_users(N_USERS)
    populate_problems(N_PROBLEMS)
