"""
schemas.py

Defines pydantic schema models that specify what fields are accepted in incoming
requests and returned in API responses.
"""

from pydantic import BaseModel, EmailStr, constr
from typing import Optional

"""
    UserCreate element types:

    * str:                    any string.
    * Emailstr:               uses email-validator meaning: must include '@'
                              and valid TLD.
    * password:               8 < pwd < 128, at least one uppercase letter,
                              at least one digit.
"""
class UserCreate(BaseModel):
    name: str
    email: Emailstr
    password: constr(
        min_length=8,
        max_length=128,
        regex="^(?=.*[A-Z])(?=.*[0-9]).+$"
    )

