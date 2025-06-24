"""
Creates a default admin user with
USERNAME: admin
PASSWORD: adminadmin
EMAIL   : email@admin.com
PERMS   : PermissionLevel.ADMIN
"""

import requests

from common.languages import Language
from common.schemas import AddProblemRequestDev
from common.typing import Difficulty


LONG_DESCRIPTION = ("An integer is received as a parameter. In your function, modify this integer "
                    "in such a way that it returns an integer that has a value of one more than "
                    "the input integer had.")


def main():
    test_exercise = AddProblemRequestDev(
        name="Add One",
        problem_id=10000,
        language=Language.C,
        difficulty=Difficulty.EASY,
        tags=[],
        short_description="Add one to input",
        long_description=LONG_DESCRIPTION,
    )

    res = requests.post(
        "http://localhost:8080/dev/add-problem",
        json=test_exercise.model_dump(),
    )
    res.raise_for_status()

    test_exercise = AddProblemRequestDev(
        name="search array",
        problem_id=10001,
        language=Language.C,
        difficulty=Difficulty.EASY,
        tags=[],
        short_description="search an array for a value",
        long_description="Search an array for a value and return the index of the value if found, ",
    )

    res = requests.post(
        "http://localhost:8080/dev/add-problem",
        json=test_exercise.model_dump(),
    )
    res.raise_for_status()


if __name__ == "__main__":
    main()
