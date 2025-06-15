"""
hasher.py

Contains functions to hash passwords with salt and check if input matches hashed password.
Used by db handler for password management.
"""

import bcrypt


def hash_password(password: str) -> bytes:
    """Hash password with salt.

    Args:
        password (str): password to be hashed

    Returns:
        bytes: hashed password with salt

    Raises:
        AssertionError: if input has incorrect typing
    """
    assert isinstance(password, str)

    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt)


def check_password(password: str, hashed_password: bytes) -> bool:
    """Check if input password after hashing matches saved hashed password.

    Args:
        password (str): input password
        hashed_password (bytes): saved hashed password

    Returns:
        bool: if password matches or not

    Raises:
        AssertionError: if input has incorrect typing
        ValueError: if hashed_password contains salt that is invalid
    """
    assert isinstance(password, str)
    assert isinstance(hashed_password, bytes)

    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)
