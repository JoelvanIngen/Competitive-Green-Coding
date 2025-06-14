import httpx

from execution_engine.config import settings
from common.schemas import SubmissionResult


async def result_to_db(res: SubmissionResult):
    async with httpx.AsyncClient() as client:
        send_result = await client.post(
            f"{settings.DB_HANDLER_URL}/api/submission_result",
            json=res,
        )

        send_result.raise_for_status()
