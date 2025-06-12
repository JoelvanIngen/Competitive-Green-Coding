import re


def check_email(email: str) -> bool:
    expression = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(expression, email):
        return True
    else:
        return False
