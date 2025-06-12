import httpx

from server.config import settings
from server.models.frontend_schemas import ProblemRequest


async def get_problem_by_id(problem_request: ProblemRequest):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{settings.DB_SERVICE_URL}/api/problem/{problem_request.problem_id}")
        res.raise_for_status()
        return res
