from app.models import Tariff
from app.repositories.tariff_repository import TariffRepository

DEFAULT_TARIFFS = (
    ("basic", 990_000),
    ("standard", 1_990_000),
    ("premium", 2_990_000),
)


class TariffService:
    def __init__(self, repository: TariffRepository) -> None:
        self.repository = repository

    async def list_tariffs(self) -> list[Tariff]:
        return await self.repository.list_tariffs()

    async def ensure_default_tariffs(self) -> None:
        await self.repository.upsert_defaults(DEFAULT_TARIFFS)
