"""
Script to populate the database with:
- Users, up to 1000
> WARNING: transform_names causes problems when creating a user]
- Problems, up to 10
> Description is always the same
> Language is always python
"""

import os
import random
import time
from uuid import uuid4

import requests

from common.languages import Language
from common.schemas import AddProblemRequestDev, RegisterRequest
from common.typing import Difficulty, PermissionLevel

LONG_DESCRIPTION = """
There are many variations of passages of Lorem Ipsum available,
but the majority have suffered alteration in some form, by injected humour,
or randomised words which don't look even slightly believable.
If you are going to use a passage of Lorem Ipsum,
you need to be sure there isn't anything embarrassing hidden in the middle of text.
All the Lorem Ipsum generators on the Internet tend to repeat predefined chunks as necessary,
making this the first true generator on the Internet.
It uses a dictionary of over 200 Latin words,
combined with a handful of model sentence structures, to generate Lorem Ipsum which looks
reasonable.
The generated Lorem Ipsum is therefore always free from repetition,
injected humour, or non-characteristic words etc.
"""

PROBLEMS = [
    {
        "name": "Two Sum",
        "description": "Find two numbers in an array that add up to a target value and return \
            their indices."
    },
    {
        "name": "Add Two Numbers",
        "description": "Add two numbers represented as linked lists where digits are stored in \
            reverse order."
    },
    {
        "name": "Longest Substring Without Repeating Characters",
        "description": "Find the length of the longest substring without duplicate characters."
    },
    {
        "name": "Median of Two Sorted Arrays",
        "description": "Find the median of two sorted arrays with O(log(m+n)) time complexity."
    },
    {
        "name": "Longest Palindromic Substring",
        "description": "Return the longest palindromic substring in a given string."
    },
    {
        "name": "Zigzag Conversion",
        "description": "Convert a string into zigzag pattern across multiple rows and read line by \
            line."
    },
    {
        "name": "Reverse Integer",
        "description": "Reverse the digits of a 32-bit signed integer, returning 0 if overflow \
            occurs."
    },
    {
        "name": "String to Integer (atoi)",
        "description": "Convert a string to a 32-bit signed integer following specific parsing \
            rules."
    },
    {
        "name": "Palindrome Number",
        "description": "Determine if an integer is a palindrome without converting it to a string."
    },
    {
        "name": "Regular Expression Matching",
        "description": "Implement regular expression matching with support for '.' and '*' \
            patterns."
    }
]

USERNAME_SUFFIXES = ['_x', '_pro', '_dev', '_gaming', '_official', '_real', '_2024', '_2023',
                     '_2022', '_2021']
USERNAME_PREFIXES = ['x_', 'the_', 'real_', 'official_', 'pro_', 'dev_']


def get_names(n_users) -> list[str]:
    """Read names from users.txt file and convert them to username-like formats"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    users_file = os.path.join(script_dir, 'users.txt')
    with open(users_file, 'r') as f:
        names = [line.strip() for line in f.readlines()]
    return names[:n_users]


def transform_names(names: list[str]) -> list[str]:
    usernames = []
    for name in names:
        use_prefix = random.random() < 0.3
        use_suffix = random.random() < 0.4
        use_number = random.random() < 0.5

        username = name.lower()

        if use_number:
            username += str(random.randint(1, 999))

        if use_prefix:
            username = random.choice(USERNAME_PREFIXES) + username

        if use_suffix:
            username += random.choice(USERNAME_SUFFIXES)

        usernames.append(username)
    return usernames


def create_users(n_users=30):
    print("Start: create_users")
    names = get_names(n_users)
    for name in names:
        print(f"name: {name} - email: {name.lower()}@hotmail.com")
        user = RegisterRequest(
            username=name,
            email=f"{name.lower()}@hotmail.com",
            password="Wafel123!",
            permission_level=PermissionLevel.USER,
        )

        res = requests.post(
            "http://localhost:8080/api/auth/register",
            json=user.model_dump(),
        )
        res.raise_for_status()
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 409:
                print(f"  ↳ {name} already in DB, skipping")
            else:
                raise e
    print("Finish: create_users")


def add_problems(n_problems=1):
    print("Start: add_problems")
    for i in range(n_problems):
        problem = AddProblemRequestDev(
            name=PROBLEMS[i]["name"],
            problem_id=i+1,
            language=Language.PYTHON,
            difficulty=random.choice([Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]),
            tags=["stani", "paki"],
            short_description=PROBLEMS[i]["description"],
            long_description=LONG_DESCRIPTION,
        )

        res = requests.post(
            "http://localhost:8080/dev/add-problem",
            json=problem.model_dump(),
        )
        res.raise_for_status()
    print("Finish: add_problems")


def login_user(username, password):
    res = requests.post(
        "http://localhost:8080/api/auth/login",
        json={"username": username, "password": password}
    )
    res.raise_for_status()
    return res.json()["access_token"]


def get_users_full():
    res = requests.get("http://localhost:8080/dev/users")
    res.raise_for_status()
    return res.json()


def submit(submission: dict, token: str):
    res = requests.post(
        "http://localhost:8080/api/submission",
        json=submission,
        headers={"Authorization": token},
    )
    res.raise_for_status()


def write_result(result: dict):
    res = requests.post(
        "http://localhost:8080/api/write-submission-result",
        json=result,
    )
    res.raise_for_status()


def create_submissions(n_problems=1):
    print("Start: create_submissions")
    users = get_users_full()  # List of dicts with uuid, username, etc.
    uuid_to_username = {user["uuid"]: user["username"] for user in users}
    uuid_to_token = {}
    for user in users:
        try:
            token = login_user(user["username"], "Wafel123!")
            uuid_to_token[user["uuid"]] = token
        except requests.HTTPError as e:
            print(f"Failed to login user {user['username']}: {e}")
            continue  # Skip this user
    for i in range(n_problems):
        for uuid in uuid_to_username:
            sub_uuid = uuid4()
            submission = {
                "submission_uuid": str(sub_uuid),
                "problem_id": i+1,
                "user_uuid": str(uuid),
                "language": "python",
                "timestamp": time.time(),
                "code": "if True: assert False",
            }
            token = uuid_to_token[uuid]
            submit(submission, token)
            result = {
                "submission_uuid": str(sub_uuid),
                "runtime_ms": float(random.randint(69, 4200)),
                "emissions_kg": float(random.randint(300, 9000)),
                "energy_usage_kwh": float(random.randint(1, 100)) / 1000.0,  # random small kWh
                "successful": True,
                "error_reason": None,
                "error_msg": None,
            }
            write_result(result)
    print("Finish: create_submissions")


def main():
    create_users()
    add_problems()
    create_submissions()


if __name__ == "__main__":
    main()
