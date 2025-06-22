"""
Creates a default admin user with
USERNAME: admin
PASSWORD: adminadmin
EMAIL   : email@admin.com
PERMS   : PermissionLevel.ADMIN
"""

import requests

from common.languages import Language
from common.schemas import RegisterRequest, AddProblemRequestDev
from common.typing import PermissionLevel


def main():
    test_exercise = AddProblemRequestDev(
        name="addOne",
        problem_id=10000,
        language=Language.C,
        difficulty="easy",
        tags=[],
        short_description="",
        long_description="",
    )

    res = requests.post(
        "http://localhost:8080/dev/add-problem",
        json=test_exercise.model_dump(),
    )
    res.raise_for_status()


if __name__ == "__main__":
    main()
