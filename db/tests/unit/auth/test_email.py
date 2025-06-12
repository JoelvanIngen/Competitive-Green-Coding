from db.auth.email import check_email

# --- FIXTURES ---


# --- NO-CRASH TEST ---
# Suffix: _pass
# Simple tests where we perform an action, and expect it to not raise an exception.
# We don't necessarily check output here (but we can if it's a one-line addition.
#   Just don't write the functions around this purpose)


def test_check_email_pass():
    check_email("")


# --- CRASH TEST ---
# Suffix _fail
# Simple tests where we perform an illegal action, and expect a specific exception
# We obviously don't check output here


# --- CODE RESULT TESTS ---
# Suffix: _result
# Simple tests where we input one thing, and assert an output or result


def test_check_valid_email_result():
    assert check_email("test.user@email.com") is True


def test_check_invalid_email_result():
    assert check_email("not_an_email") is False
    assert check_email("") is False


# --- CODE FLOW TESTS ---
# Suffix: _mocker
# Tests where we follow the code flow using the mocker
