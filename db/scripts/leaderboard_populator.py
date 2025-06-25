"""
Creates
- 30 users
- 1 problem
- 1 submission per user
"""

import random, requests, string, os
from uuid import UUID, uuid4

from common.schemas import (
    RegisterRequest,
    AddProblemRequestDev,
    SubmissionCreate,
    SubmissionResult,
)
from common.typing import PermissionLevel, Difficulty
from common.languages import Language


LONG_DESCRIPTION = """
There are many variations of passages of Lorem Ipsum available,
but the majority have suffered alteration in some form, by injected humour,
or randomised words which don't look even slightly believable.
If you are going to use a passage of Lorem Ipsum,
you need to be sure there isn't anything embarrassing hidden in the middle of text.
All the Lorem Ipsum generators on the Internet tend to repeat predefined chunks as necessary,
making this the first true generator on the Internet.
It uses a dictionary of over 200 Latin words,
combined with a handful of model sentence structures, to generate Lorem Ipsum which looks reasonable.
The generated Lorem Ipsum is therefore always free from repetition,
injected humour, or non-characteristic words etc.
"""

PROBLEMS = [
    {
        "name": "Two Sum",
        "description": "Find two numbers in an array that add up to a target value and return their indices."
    },
    {
        "name": "Add Two Numbers",
        "description": "Add two numbers represented as linked lists where digits are stored in reverse order."
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
        "description": "Convert a string into zigzag pattern across multiple rows and read line by line."
    },
    {
        "name": "Reverse Integer",
        "description": "Reverse the digits of a 32-bit signed integer, returning 0 if overflow occurs."
    },
    {
        "name": "String to Integer (atoi)",
        "description": "Convert a string to a 32-bit signed integer following specific parsing rules."
    },
    {
        "name": "Palindrome Number",
        "description": "Determine if an integer is a palindrome without converting it to a string."
    },
    {
        "name": "Regular Expression Matching",
        "description": "Implement regular expression matching with support for '.' and '*' patterns."
    }
]

USERNAME_SUFFIXES = ['_x', '_pro', '_dev', '_gaming', '_official', '_real', '_2024', '_2023', '_2022', '_2021']
USERNAME_PREFIXES = ['x_', 'the_', 'real_', 'official_', 'pro_', 'dev_']

def get_names(n_users) -> list[str]:
    """Read names from users.txt file and convert them to username-like formats"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    users_file = os.path.join(script_dir, 'users.txt')
    with open(users_file, 'r') as f:
        names = [line.strip() for line in f.readlines()]

    # Transform names into username-like formats
    names = names[:n_users]
    # usernames = []
    # for name in names:
    #     use_prefix = random.random() < 0.3
    #     use_suffix = random.random() < 0.4
    #     use_number = random.random() < 0.5

    #     username = name.lower()

    #     if use_number:
    #         username += str(random.randint(1, 999))

    #     if use_prefix:
    #         username = random.choice(USERNAME_PREFIXES) + username

    #     if use_suffix:
    #         username += random.choice(USERNAME_SUFFIXES)

    #     usernames.append(username)

    return names


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


def get_users():
    res = requests.get(
            "http://localhost:8080/dev/dev/users",
        )
    res.raise_for_status()
    users = res.json()
    user_ids = [user["uuid"] for user in users]
    return user_ids


def submit(submission: SubmissionCreate):
    res = requests.post(
            "http://localhost:8080/api/submission",
            json=submission.model_dump(),
        )
    res.raise_for_status()


def write_result(result: SubmissionResult):
    res = requests.post(
            "http://localhost:8080/api/write-submission-result",
            json=result.model_dump(),
        )
    res.raise_for_status()


def create_submissions(n_problems=1):
    print("Start: create_submissions")
    user_ids = get_users()
    print(f"Users: {user_ids}")
    for i in range(n_problems):
        for uuid in user_ids:
            sub_uuid = uuid4()
            submission = SubmissionCreate(
                submission_uuid=sub_uuid,
                problem_id=i+1,
                user_uuid=UUID(uuid),
                language=Language.PYTHON,
                timestamp=float(random.randint(0, 1000)),
                code="if True: assert False"
            )
            submit(submission)

            result = SubmissionResult(
                submission_uuid=sub_uuid,
                runtime_ms=float(random.randint(69, 4200)),
                mem_usage_mb=float(random.randint(300, 9000)),
                successful=True,
                error_reason=None,
                error_msg=None,
            )
            write_result(result)
    print("Finish: create_submissions")


def main():
    create_users()
    add_problems()
    create_submissions()


if __name__ == "__main__":
    main()