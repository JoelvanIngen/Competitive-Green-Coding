from fastapi import HTTPException
from sqlmodel import Session

from common.schemas import AddProblemRequestDev, ProblemDetailsResponse
from common.typing import Difficulty
from db.engine import queries
from db.engine.queries import DBCommitError
from db.models.convert import db_problem_to_problem_get
from db.models.db_schemas import ProblemEntry, ProblemTagEntry


def _commit_or_500(session: Session, entry):
    """
    Attempts to commit the given entry to the database.
    :raises HTTPException 500: On DB error.
    """
    try:
        queries.commit_entry(session, entry)
    except DBCommitError as e:
        raise HTTPException(status_code=500, detail="Internal server error") from e


def create_problem(s: Session, problem: AddProblemRequestDev) -> ProblemDetailsResponse:
    """Create problem without admin permissions

    Args:
        s (Session): session to communicate with the database
        problem (AddProblemRequestDev): problem to create

    Raises:
        HTTPException: 400 if problem is not valid

    Returns:
        ProblemDetailsResponse: data of generated problem
    """
    if problem.difficulty not in Difficulty.to_list() or not problem.name:
        raise HTTPException(
            status_code=400,
            detail="ERROR_VALIDATION_FAILED",
        )

    problem_entry = ProblemEntry(
        problem_id=problem.problem_id,
        name=problem.name,  # pylint: disable=R0801
        language=problem.language,
        difficulty=problem.difficulty,
        short_description=problem.short_description,
        long_description=problem.long_description,
        template_code="",
    )

    _commit_or_500(s, problem_entry)

    for tag in problem.tags:
        problem_tag_entry = ProblemTagEntry(problem_id=problem.problem_id, tag=tag)
        _commit_or_500(s, problem_tag_entry)

    s.refresh(problem_entry)

    problem_get = db_problem_to_problem_get(problem_entry)

    return problem_get
