"""
This module will store any types created for this module.
"""

from typing import Annotated, TypeAlias

from fastapi import Depends
from sqlmodel import Session

from db.engine import get_session
from db.models.db_schemas import ProblemEntry, ProblemTagEntry, SubmissionEntry, UserEntry

__all__ = ["SessionDep", "DBEntry"]

SessionDep = Annotated[Session, Depends(get_session)]
DBEntry: TypeAlias = UserEntry | ProblemEntry | SubmissionEntry | ProblemTagEntry
