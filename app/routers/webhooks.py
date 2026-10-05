from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_session
from app.repositories.payment_repository import PaymentRepository
from app.schemas import (
    BankWebhookRequest,
    InvalidTransitResponse,
    WebhookSuccessResponse,
)
from app.services.webhook_service import (
    InvalidTransitionError,
    PaymentNotFoundError,
    WebhookService,
)

SessionDep = Annotated[AsyncSession, Depends(get_session, scope="function")]

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post(
    "/bank",
    response_model=WebhookSuccessResponse,
    responses={
        404: {"description": "Payment not found"},
        409: {"model": InvalidTransitResponse},
    },
)
async def bank_webhook(
    data: BankWebhookRequest, session: SessionDep
) -> dict[str, str] | JSONResponse:
    service = WebhookService(PaymentRepository(session))
    try:
        await service.change_status(data.payment_id, data.status)
    except PaymentNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Payment not found") from exc
    except InvalidTransitionError:
        return JSONResponse(
            status_code=409, content={"error": "invalid_transition"}
        )
    return {"result": "ok"}