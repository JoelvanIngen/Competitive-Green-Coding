import re


def check_email(email: str) -> bool:
    """Checks if email is a valid email.

    Args:
        email (str): input email

    Returns:
        bool: if email matches constraints
    """
    expression = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    return bool(re.fullmatch(expression, email) and len(email) <= 64)


def check_username(username: str) -> bool:
    """Checks if username is alphanumeric and between 2-32 characters long.

    Args:
        username (str): input username

    Returns:
        bool: if username matches constraints
    """
    expression = r"\b[A-Za-z0-9]{2,32}\b"
    return bool(re.fullmatch(expression, username))
