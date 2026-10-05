from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_session
from app.models import Tariff
from app.repositories.tariff_repository import TariffRepository
from app.schemas import TariffResponse
from app.services.tariff_service import TariffService

SessionDep = Annotated[AsyncSession, Depends(get_session)]

router = APIRouter(
    prefix="/tariffs",
    tags=["tariffs"],
)


@router.get("", response_model=list[TariffResponse])
async def get_tariffs(session: SessionDep) -> list[Tariff]:
    repository = TariffRepository(session)
    service = TariffService(repository)
    return await service.list_tariffs()
