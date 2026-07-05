from fastapi import APIRouter, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.dto.healthcheck import HealthcheckResponse
from app.services.healthcheck import check_postgres, check_redis
from app.services.redis import RedisRepository

router: APIRouter = APIRouter(prefix="/health")


@router.get(path="/liveness")
async def handle_liveness() -> HealthcheckResponse:
    return HealthcheckResponse.alive(service="bot")


@router.get(path="/readiness")
async def handle_readiness(request: Request, response: Response) -> HealthcheckResponse:
    redis: RedisRepository = request.app.state.redis_repository
    session_pool: async_sessionmaker[AsyncSession] = request.app.state.session_pool
    response_body: HealthcheckResponse = HealthcheckResponse.ready(service="bot", ready=True)
    if request.app.state.shutdown_completed:
        response_body = HealthcheckResponse.ready(service="bot", ready=False)
    else:
        await check_redis(response=response_body, redis=redis)
        await check_postgres(response=response_body, session_pool=session_pool)
    response.status_code = response_body.get_status_code()
    return response_body
