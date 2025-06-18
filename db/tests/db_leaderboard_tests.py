import os
import random
import string

import requests
from config import HOST, PORT
from loguru import logger

URL = f"http://{HOST}:{PORT}/api"
PROBLEM_NAMES = ["aap", "noot", "mies", "wim", "zus",
                 "jet", "teun", "vuur", "gijs", "lam",
                 "kees", "bok", "weide", "does", "hok",
                 "duif", "schapen", "zonamo", "feyenoord", "duizend"]


def get_names():
    """Read names from users.txt file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    users_file = os.path.join(script_dir, 'users.txt')
    with open(users_file, 'r') as f:
        return [line.strip() for line in f.readlines()]


def populate_db(create_users=True, create_problems=True, problems_limit=3):
    """Populate the database with test data"""
    names = get_names()

    # Create users
    uuids = []
    if create_users:
        for name in names:  # More users than in insert test
            password = "".join(random.choices(string.ascii_letters, k=32))

            data = {
                "username": name,
                "email": f"{name.lower()}@hotmail.com",
                "password_hash": password
            }

            entry = requests.post(f'{URL}/users/', json=data).json()
            uuids.append(entry["uuid"])
        logger.info("Populated Users")
    else:  # Get existing users
        users = requests.get(f'{URL}/users').json()
        uuids = [user["uuid"] for user in users]
        logger.info(f"Retrieved {len(uuids)} existing users")

    # Create problems
    pids = []
    if create_problems:
        for i in range(10):  # Create exactly 10 problems
            name = f"{PROBLEM_NAMES[i]} problem #{i}"
            tags = [random.choice(['C', 'python'])]

            data = {
                "name": name,
                "tags": tags,
                "description": "test description"
            }

            entry = requests.post(f'{URL}/problems/', json=data).json()
            pids.append(entry["problem_id"])
        logger.info("Populated Problems")
    else:  # Get existing problems
        problems = requests.get(f'{URL}/problems').json()
        pids = [problem["problem_id"] for problem in problems]
        logger.info(f"Retrieved {len(pids)} existing problems")

    # Create submissions with varying success rates
    submissions = []
    for uuid in uuids:
        for pid in pids[:problems_limit]:
            if random.random() < 0.8:
                successful = random.random() < 0.8
                score = random.randint(1, 10) if successful else 0

                data = {
                    "problem_id": pid,
                    "uuid": uuid,
                    "timestamp": random.randint(0, 1000),
                    "code": f"{pid}_code.md",
                    "successful": successful,
                    "score": score,
                }

                submissions.append(data)

    for sub in submissions:
        response = requests.post(f'{URL}/submissions/', json=sub)
        if response.status_code != 200:
            logger.error(f"Failed to create submission: {response.text}")

    logger.info(f"Finished creating {len(submissions)} total submissions")


def test_get_leaderboard():
    """Test the leaderboard endpoint"""

    # Get the leaderboard
    response = requests.get(f'{URL}/leaderboard')
    assert response.status_code == 200

    leaderboard = response.json()

    # Verify the response structure
    assert "entries" in leaderboard
    assert isinstance(leaderboard["entries"], list)

    # Verify each entry has the required fields
    for entry in leaderboard["entries"]:
        assert "username" in entry
        assert "total_score" in entry
        assert "problems_solved" in entry
        assert isinstance(entry["total_score"], (int, float))
        assert isinstance(entry["problems_solved"], int)

    # Verify that no person with 0 problems solved appears on the leaderboard
    for entry in leaderboard["entries"]:
        assert entry["problems_solved"] > 0, \
            f"{entry['username']} solved 0 problems"

    # Verify the leaderboard is sorted by total_score in descending order
    scores = [entry["total_score"] for entry in leaderboard["entries"]]
    assert scores == sorted(scores, reverse=True)

    return leaderboard


if __name__ == "__main__":
    # populate_db()
    leaderboard = test_get_leaderboard()
