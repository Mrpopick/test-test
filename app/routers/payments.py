from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_session
from app.models import Payment
from app.repositories.payment_repository import PaymentRepository
from app.schemas import PaymentResponse, PaymentCreateRequest
from app.services.payment_service import PaymentService, TariffNotFoundError

SessionDep = Annotated[AsyncSession, Depends(get_session, scope="function")]

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: int, session: SessionDep) -> Payment:
    service = PaymentService(PaymentRepository(session))
    payment = await service.get_payment(payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.post(
    "",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    responses={200: {"model": PaymentResponse}},
)
async def create_payment(
    data: PaymentCreateRequest,
    session: SessionDep,
    response: Response,
    idempotency_key: Annotated[
        str | None, Header(alias="Idempotency-Key", min_length=1, max_length=255)
    ] = None,
) -> Payment:
    service = PaymentService(PaymentRepository(session))
    try:
        payment, created = await service.create_payment(data, idempotency_key)
    except TariffNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Tariff not found") from exc

    if not created:
        response.status_code = status.HTTP_200_OK
    return payment
