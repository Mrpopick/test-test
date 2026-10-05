from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, async_session_factory, engine
from app.repositories.tariff_repository import TariffRepository
from app.routers.payments import router as payments_router
from app.routers.tariffs import router as tariffs_router
from app.routers.webhooks import router as webhooks_router
from app.services.tariff_service import TariffService


async def initialize_database() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        async with session.begin():
            service = TariffService(TariffRepository(session))
            await service.ensure_default_tariffs()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    try:
        await initialize_database()
        yield
    finally:
        await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title="test_api", version="0.1.0", lifespan=lifespan)
    app.include_router(tariffs_router)
    app.include_router(payments_router)
    app.include_router(webhooks_router)

    @app.get("/health", tags=["health"])
    async def get_health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()