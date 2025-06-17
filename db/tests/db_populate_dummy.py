"""Database Population Script

This script populates the database with test data including users, problems, and submissions.
You can customize the amount of data created using command-line arguments:

Usage:
    python db_populate_dummy.py [--users NUM] [--problems NUM] [--submissions NUM]

Options:
    --users NUM       Number of users to create (default: all from users.txt)
    --problems NUM    Number of problems to create (default: 10, max: 10)
    --submissions NUM Number of problems each user will submit to (default: 3)

Example:
    python db_populate_dummy.py --users 50 --problems 5 --submissions 2
"""

import argparse
import os
import random
import string

import requests
from config import HOST, PORT
from loguru import logger

URL = f"http://{HOST}:{PORT}/api"

PROBLEMS = [
    {
        "name": "Two Sum",
        "description": "Find two numbers in an array that add up to a target value and return their indices.",
        "difficulty": "Easy"
    },
    {
        "name": "Add Two Numbers",
        "description": "Add two numbers represented as linked lists where digits are stored in reverse order.",
        "difficulty": "Medium"
    },
    {
        "name": "Longest Substring Without Repeating Characters",
        "description": "Find the length of the longest substring without duplicate characters.",
        "difficulty": "Medium"
    },
    {
        "name": "Median of Two Sorted Arrays",
        "description": "Find the median of two sorted arrays with O(log(m+n)) time complexity.",
        "difficulty": "Hard"
    },
    {
        "name": "Longest Palindromic Substring",
        "description": "Return the longest palindromic substring in a given string.",
        "difficulty": "Medium"
    },
    {
        "name": "Zigzag Conversion",
        "description": "Convert a string into zigzag pattern across multiple rows and read line by line.",
        "difficulty": "Medium"
    },
    {
        "name": "Reverse Integer",
        "description": "Reverse the digits of a 32-bit signed integer, returning 0 if overflow occurs.",
        "difficulty": "Medium"
    },
    {
        "name": "String to Integer (atoi)",
        "description": "Convert a string to a 32-bit signed integer following specific parsing rules.",
        "difficulty": "Medium"
    },
    {
        "name": "Palindrome Number",
        "description": "Determine if an integer is a palindrome without converting it to a string.",
        "difficulty": "Easy"
    },
    {
        "name": "Regular Expression Matching",
        "description": "Implement regular expression matching with support for '.' and '*' patterns.",
        "difficulty": "Hard"
    }
]

USERNAME_SUFFIXES = ['_x', '_pro', '_dev', '_gaming', '_official', '_real', '_2024', '_2023', '_2022', '_2021']
USERNAME_PREFIXES = ['x_', 'the_', 'real_', 'official_', 'pro_', 'dev_']

def get_names():
    """Read names from users.txt file and convert them to username-like formats"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    users_file = os.path.join(script_dir, 'users.txt')
    with open(users_file, 'r') as f:
        names = [line.strip() for line in f.readlines()]

    # Transform names into username-like formats
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


def populate_db(num_users=None, num_problems=10, submission_limit=3):
    """Populate the database with test data

    Args:
        num_users (int, optional): Number of users to create. If None, creates all users from users.txt
        num_problems (int): Number of problems to create (max 10)
        problems_limit (int): Number of problems each user will submit to
    """
    names = get_names()
    if num_users is not None:
        names = names[:num_users]

    # Create users
    uuids = []
    for name in names:
        password = "".join(random.choices(string.ascii_letters, k=32))

        data = {
            "username": name,
            "email": f"{name.lower()}@hotmail.com",
            "password": password,
            "permission_level": "user"
        }

        entry = requests.post(f'{URL}/auth/register/', json=data).json()
        uuids.append(entry["uuid"])
    logger.info(f"Populated {len(uuids)} Users")

    # Create problems
    for problem in PROBLEMS[:num_problems]:
        tags = [random.choice(['C', 'python'])]  # TODO: Add difficulty tags when db is updated

        data = {
            "name": problem["name"],
            "tags": tags,
            "description": problem["description"]
        }

        entry = requests.post(f'{URL}/problems/', json=data).json()
    logger.info(f"Populated {len(PROBLEMS[:num_problems])} Problems")

    # Create submissions with varying success rates
    submissions = []
    for uuid in uuids:
        for pid in range(1, submission_limit+1):
            if random.random() < 0.8:
                successful = random.random() < 0.8
                runtime_ms = random.randint(69, 4200) if successful else 0

                data = {
                    "problem_id": pid,
                    "uuid": uuid,
                    "runtime_ms": runtime_ms,
                    "timestamp": random.randint(0, 1000),
                    "successful": successful,
                    "code": f"{uuid}_{pid}_code.md",
                }

                submissions.append(data)

    for sub in submissions:
        response = requests.post(f'{URL}/submissions/', json=sub)
        if response.status_code != 200:
            logger.error(f"Failed to create submission: {response.text}")

    logger.info(f"Finished creating {len(submissions)} total submissions")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Populate the database with test data')
    parser.add_argument('--users', type=int, help='Number of users to create (default: all from users.txt)')
    parser.add_argument('--problems', type=int, default=10,
                      help='Number of problems to create (default: 10, max: 10)')
    parser.add_argument('--submissions', type=int, default=3,
                      help='Number of problems each user will submit to (default: 3)')

    args = parser.parse_args()

    # Validate arguments
    if args.problems > 10:
        logger.warning("Maximum number of problems is 10. Setting to 10.")
        args.problems = 10

    if args.submissions > args.problems:
        logger.warning(f"Number of submissions ({args.submissions}) cannot be greater than number of problems ({args.problems}). Setting to {args.problems}.")
        args.submissions = args.problems

    logger.info(f"Starting database population with:")
    logger.info(f"- Users: {args.users if args.users else 'all from users.txt'}")
    logger.info(f"- Problems: {args.problems}")
    logger.info(f"- Submissions per user: {args.submissions}")

    populate_db(num_users=args.users, num_problems=args.problems, submission_limit=args.submissions)
