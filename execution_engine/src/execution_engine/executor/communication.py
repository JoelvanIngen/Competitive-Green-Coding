import httpx
from loguru import logger

from common.schemas import SubmissionResult
from execution_engine.config import settings


async def result_to_db(res: SubmissionResult):
    logger.info(f"Task finished, result:\n{res}")

    async with httpx.AsyncClient() as client:
        send_result = await client.post(
            f"{settings.DB_HANDLER_URL}/api/write-submission-result",
            content=res.model_dump_json(),
            headers={"Content-Type": "application/json"},
        )

        send_result.raise_for_status()
