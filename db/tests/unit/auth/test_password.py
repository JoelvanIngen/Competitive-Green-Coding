import random
import string

import pytest

from common.auth import check_password, hash_password

# --- FIXTURES ---


@pytest.fixture(name="correct_password")
def correct_password_fixture():
    return ''.join(random.choices(string.digits + string.ascii_letters, k=32))


@pytest.fixture(name="incorrect_password")
def incorrect_password_fixture():
    return ''.join(random.choices(string.digits + string.ascii_letters, k=32))


# --- NO-CRASH TEST ---
# Suffix: _pass
# Simple tests where we perform an action, and expect it to not raise an exception.
# We don't necessarily check output here (but we can if it's a one-line addition.
#   Just don't write the functions around this purpose)


def test_hash_password_pass(correct_password: str):
    """Test if hash_password() passes when correct input is used.

    Args:
        correct_password (str): input password
    """
    hash_password(correct_password)


def test_check_password_pass(correct_password: str):
    """Test if check_password() passes when correct input is used.

    Args:
        correct_password (str): input password
    """
    hashed_password = hash_password(correct_password)
    check_password(correct_password, hashed_password)


# --- CRASH TEST ---
# Suffix _fail
# Simple tests where we perform an illegal action, and expect a specific exception
# We obviously don't check output here


def test_hash_password_incorrect_input_fail():
    """Test if hash_password() raises AssertionError if input is not a string.
    """
    with pytest.raises(AssertionError):
        hash_password(0)


def test_check_password_incorrect_input_fail(correct_password: str):
    """Check if check_password() raises AssertionError if input is not a (string, bytes).

    Args:
        correct_password (str): input password
    """
    hashed_password = hash_password(correct_password)

    with pytest.raises(AssertionError):
        check_password(0, hashed_password)

    with pytest.raises(AssertionError):
        check_password("", "")


def test_check_password_no_salt_fail(correct_password: str):
    """Check if check_password() raises ValueError if hashed password is not really a hashed
    password.
    """
    with pytest.raises(ValueError):
        check_password("", bytes())


# --- CODE RESULT TESTS ---
# Suffix: _result
# Simple tests where we input one thing, and assert an output or result


def test_check_password_correct_result(correct_password: str):
    """Check if check_password() returns True if password is correct

    Args:
        correct_password (str): input password
    """
    hashed_password = hash_password(correct_password)

    assert isinstance(hashed_password, bytes)
    assert check_password(correct_password, hashed_password) is True


def test_check_password_incorrect_result(correct_password: str, incorrect_password: str):
    """Check if check_password() returns True if password is correct

    Args:
        correct_password (str): input password
        incorrect_password (str): incorrect password
    """
    hashed_password = hash_password(correct_password)

    assert isinstance(hashed_password, bytes)
    assert check_password(incorrect_password, hashed_password) is False


# --- CODE FLOW TESTS ---
# Suffix: _mocker
# Tests where we follow the code flow using the mocker
