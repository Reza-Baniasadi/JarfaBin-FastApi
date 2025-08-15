from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from typing import Any

import fastapi
import redis.asyncio as redis
from arq import create_pool
from arq.connections import RedisSettings
from fastapi import APIRouter, Depends, FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from ..api.dependencies import get_current_superuser
from ..core.utils.rate_limit import rate_limiter
from ..middleware.client_cache_middleware import ClientCacheMiddleware
from ..models import Base
from .config import (
    AppSettings,
    ClientSideCacheSettings,
    DatabaseSettings,
    EnvironmentOption,
    EnvironmentSettings,
    RedisCacheSettings,
    RedisQueueSettings,
    RedisRateLimiterSettings,
    settings,
)
from .db.database import async_engine as engine
from .utils import cache, queue


async def init_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def init_redis_cache() -> None:
    cache.pool = redis.ConnectionPool.from_url(settings.REDIS_CACHE_URL)
    cache.client = redis.Redis.from_pool(cache.pool)


async def close_redis_cache() -> None:
    if cache.client:
        await cache.client.aclose()


async def init_redis_queue() -> None:
    queue.pool = await create_pool(
        RedisSettings(host=settings.REDIS_QUEUE_HOST, port=settings.REDIS_QUEUE_PORT)
    )


async def close_redis_queue() -> None:
    if queue.pool:
        await queue.pool.aclose()


async def init_redis_rate_limiter() -> None:
    rate_limiter.initialize(settings.REDIS_RATE_LIMIT_URL)


def lifespan_factory(
    settings: Any,
    create_tables_on_start: bool = True,
) -> Callable[[FastAPI], AsyncGenerator[Any, None]]:

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[Any, None]:
        from asyncio import Event

        app.state.initialization_complete = Event()

        if isinstance(settings, RedisCacheSettings):
            await init_redis_cache()
        if isinstance(settings, RedisQueueSettings):
            await init_redis_queue()
        if isinstance(settings, RedisRateLimiterSettings):
            await init_redis_rate_limiter()
        if create_tables_on_start:
            await init_database()

        app.state.initialization_complete.set()

        try:
            yield
        finally:
            if isinstance(settings, RedisCacheSettings):
                await close_redis_cache()
            if isinstance(settings, RedisQueueSettings):
                await close_redis_queue()
            if isinstance(settings, RedisRateLimiterSettings):
                await create_redis_rate_limiter()

    return lifespan


def create_application(
    router: APIRouter,
    settings: Any,
    create_tables_on_start: bool = True,
    lifespan: Callable[[FastAPI], AsyncGenerator[Any, None]] | None = None,
    **kwargs: Any,
) -> FastAPI:

    if isinstance(settings, AppSettings):
        kwargs.update({
            "title": settings.APP_NAME,
            "description": settings.APP_DESCRIPTION,
            "contact": {"name": settings.CONTACT_NAME, "email": settings.CONTACT_EMAIL},
            "license_info": {"name": settings.LICENSE_NAME},
        })

    if isinstance(settings, EnvironmentSettings):
        kwargs.update({"docs_url": None, "redoc_url": None, "openapi_url": None})

    if lifespan is None:
        lifespan = lifespan_factory(settings, create_tables_on_start=create_tables_on_start)

    app = FastAPI(lifespan=lifespan, **kwargs)
    app.include_router(router)

    if isinstance(settings, ClientSideCacheSettings):
        app.add_middleware(ClientCacheMiddleware, max_age=settings.CLIENT_CACHE_MAX_AGE)

    if isinstance(settings, EnvironmentSettings) and settings.ENVIRONMENT != EnvironmentOption.PRODUCTION:
        docs_router = APIRouter()
        if settings.ENVIRONMENT != EnvironmentOption.LOCAL:
            docs_router = APIRouter(dependencies=[Depends(get_current_superuser)])

        @docs_router.get("/docs", include_in_schema=False)
        async def swagger_docs() -> fastapi.responses.HTMLResponse:
            return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")

        @docs_router.get("/redoc", include_in_schema=False)
        async def redoc_docs() -> fastapi.responses.HTMLResponse:
            return get_redoc_html(openapi_url="/openapi.json", title="docs")

        @docs_router.get("/openapi.json", include_in_schema=False)
        async def openapi_schema() -> dict[str, Any]:
            return get_openapi(title=app.title, version=app.version, routes=app.routes)

        app.include_router(docs_router)

    return app
