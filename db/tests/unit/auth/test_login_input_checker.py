from db.auth.login_input_checker import check_email, check_username

# --- FIXTURES ---


# --- NO-CRASH TEST ---
# Suffix: _pass
# Simple tests where we perform an action, and expect it to not raise an exception.
# We don't necessarily check output here (but we can if it's a one-line addition.
#   Just don't write the functions around this purpose)


def test_check_email_pass():
    check_email("")


def test_check_username_pass():
    check_username("")


# --- CRASH TEST ---
# Suffix _fail
# Simple tests where we perform an illegal action, and expect a specific exception
# We obviously don't check output here


# --- CODE RESULT TESTS ---
# Suffix: _result
# Simple tests where we input one thing, and assert an output or result


def test_check_valid_email_result():
    assert check_email("test.user@email.com") is True


def test_check_valid_username_result():
    assert check_username("TestUser") is True
    assert check_username("TestUser1234") is True


def test_check_invalid_email_result():
    assert check_email("not_an_email") is False
    assert check_email("") is False


def test_check_invalid_username_result():
    assert check_username("a") is False
    assert check_username("TestUser1234567891011121314151617") is False


# --- CODE FLOW TESTS ---
# Suffix: _mocker
# Tests where we follow the code flow using the mocker
