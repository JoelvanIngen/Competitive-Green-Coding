from datetime import datetime
from uuid import UUID, uuid4

# import httpx

from common.auth import jwt_to_data
from common.schemas import (
    ProblemRequest,
    SubmissionCreate,
    SubmissionRequest,
)
from server.api.proxy import db_request
from server.config import settings


async def get_problem_by_id(problem_request: ProblemRequest, auth_header: dict[str, str]):
    res = await db_request(
        "get",
        f"/problems/{problem_request.problem_id}",
        headers=auth_header,
    )

    res.raise_for_status()
    return res.json()


async def post_submission(submission: SubmissionRequest, auth_header: dict[str, str], token: str):
    # Create SubmissionCreate model
    # sub_create = SubmissionCreate(
    #     submission_uuid=uuid4(),
    #     problem_id=submission.problem_id,
    #     user_uuid=UUID(jwt_to_data(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM).uuid),
    #     language=submission.language,
    #     timestamp=float(datetime.now().timestamp()),
    #     code=submission.code,
    # )

    sub_create = {
        "submission_uuid": str(uuid4()),
        "problem_id": submission.problem_id,
        "user_uuid": jwt_to_data(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM).uuid,
        "language": submission.language,
        "timestamp": float(datetime.now().timestamp()),
        "code": submission.code,
    }

    # Send initial submission to DB
    submission_res = await db_request(
        "post",
        "/submission",
        headers=auth_header,
        json_payload=sub_create,
    )

    return submission_res.json()

    # # Send submission to engine
    # async with httpx.AsyncClient() as client:
    #     _ = await client.post(
    #         f"{settings.ENGINE_URL}/api/execute",
    #         json=sub_create.model_dump(),
    #     )

    # # res.raise_for_status()
