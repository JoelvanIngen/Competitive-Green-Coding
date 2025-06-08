"""
This module will store any types created for this module.
"""

from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from db.engine import get_session

__all__ = ["SessionDep"]

SessionDep = Annotated[Session, Depends(get_session)]
