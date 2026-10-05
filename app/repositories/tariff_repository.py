from collections.abc import Sequence
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Tariff


class TariffRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_tariffs(self) -> list[Tariff]:
        result = await self.session.scalars(
            select(Tariff).order_by(Tariff.price, Tariff.title)
        )
        return list(result.all())

    async def upsert_defaults(self, tariffs: Sequence[tuple[str, int]]) -> None:
        values = [
            {"id": uuid4(), "title": title, "price": price}
            for title, price in tariffs
        ]
        statement = insert(Tariff).values(values)
        statement = statement.on_conflict_do_update(
            index_elements=[Tariff.title],
            set_={"price": statement.excluded.price},
        )
        await self.session.execute(statement)
