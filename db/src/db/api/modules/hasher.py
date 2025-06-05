import bcrypt


def hash_password(password: str) -> bytearray:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

    return hashed_password


def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)


if __name__ == "__main__":
    hashed_password = hash_password("test_password1")
    print(check_password("test_password1", hashed_password))
    print(check_password("test_password2", hashed_password))
