from datetime import datetime
from uuid import uuid4

import httpx

from common.schemas import ProblemRequest, SubmissionCreate, SubmissionRequest
from server.api.proxy import db_request
from server.config import settings


async def get_problem_by_id(problem_request: ProblemRequest):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{settings.DB_SERVICE_URL}/api/problems/{problem_request.problem_id}"
        )
        res.raise_for_status()
        return res


async def post_submission(submission: SubmissionRequest, auth_header: dict, token: str):
    # Create SubmissionCreate model
    sub_create = SubmissionCreate(
        submission_uuid=uuid4(),
        problem_id=submission.problem_id,
        user_uuid=uuid4(),  # TODO: placeholder, use JWT decode function
        language=submission.language,  # TODO: Doesn't exist, we need to lookup the exercice name
        timestamp=int(datetime.now().timestamp()),
        code=submission.code,
    )

    # Send initial submission to DB
    res = await db_request(
        "post",
        "/submission",
        headers=auth_header,
        json_payload=sub_create.model_dump(),
    )

    res.raise_for_status()

    # Send submission to engine
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{settings.ENGINE_URL}/api/execute",
            json=sub_create.model_dump(),
        )

    res.raise_for_status()

    # Engine returns 201 Created, we are done
    # Front-end can now perform submission lookups to check if execution is completed already
