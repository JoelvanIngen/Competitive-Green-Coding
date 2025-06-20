"""
Creates a default admin user with
USERNAME: admin
PASSWORD: adminadmin
EMAIL   : email@admin.com
PERMS   : PermissionLevel.ADMIN
"""

import requests

from common.schemas import RegisterRequest
from common.typing import PermissionLevel


def main():
    admin_user = RegisterRequest(
        username="admin",
        email="email@admin.com",
        password="adminadmin",
        permission_level=PermissionLevel.ADMIN,
    )

    res = requests.post(
        "http://localhost:8080/api/auth/register",
        json=admin_user.model_dump(),
    )
    res.raise_for_status()


if __name__ == "__main__":
    main()
