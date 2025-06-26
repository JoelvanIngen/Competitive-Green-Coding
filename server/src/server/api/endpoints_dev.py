from fastapi import APIRouter

from common.schemas import SubmissionResult
from server.api import proxy

router = APIRouter()


@router.post("/write-submission-result")
async def add_problem(submission_result: SubmissionResult):
    result = {
        "submission_uuid": str(submission_result.submission_uuid),
        "runtime_ms": submission_result.runtime_ms,
        "emissions_kg": submission_result.emissions_kg,
        "energy_usage_kwh": submission_result.energy_usage_kwh,
        "successful": submission_result.successful,
        "error_reason": submission_result.error_reason,
        "error_msg": submission_result.error_msg,
    }

    await proxy.db_request(
        "post",
        "/write-submission-result",
        json_payload=result,
    )
