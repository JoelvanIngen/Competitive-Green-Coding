from fastapi import APIRouter
from server.api import proxy

from common.schemas import SubmissionResult

router = APIRouter()


@router.post("/dev/write-submission-result")
async def add_problem(submission_result: SubmissionResult):
    submission_result = {
        "submission_uuid": str(submission_result.submission_uuid),
        "runtime_ms": submission_result.runtime_ms,
        "mem_usage_mb": submission_result.mem_usage_mb,
        "energy_usage_kwh": submission_result.energy_usage_kwh,
        "successful": submission_result.successful,
        "error_reason": submission_result.error_reason,
        "error_msg": submission_result.error_msg
    }

    await proxy.db_request(
        'post',
        '/write-submission-result',
        json_payload=submission_result,
    )
