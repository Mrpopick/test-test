from typing import Literal

from app.repositories.payment_repository import PaymentRepository


ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    "pending": frozenset({"succeeded", "failed"}),
    "succeeded": frozenset({"refunded"}),
}
PaymentStatus = Literal["pending", "succeeded", "failed", "refunded"]


class PaymentNotFoundError(Exception):
    pass


class InvalidTransitionError(Exception):
    pass


class WebhookService:
    def __init__(self, repository: PaymentRepository) -> None:
        self.repository = repository

    async def change_status(self, payment_id: int, new_status: PaymentStatus) -> None:
        payment = await self.repository.get(payment_id)
        if payment is None:
            raise PaymentNotFoundError
        if new_status not in ALLOWED_TRANSITIONS.get(payment.status, frozenset()):
            raise InvalidTransitionError
        payment.status = new_status
