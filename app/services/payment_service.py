from app.models import Payment
from app.price_services.pricing import build_schedule, calculate_price
from app.repositories.payment_repository import PaymentRepository
from app.schemas import PaymentCreateRequest


class TariffNotFoundError(Exception):
    pass


class PaymentService:
    def __init__(self, repository: PaymentRepository) -> None:
        self.repository = repository

    async def get_payment(self, payment_id: int) -> Payment | None:
        return await self.repository.get(payment_id)

    async def create_payment(
        self, data: PaymentCreateRequest, idempotency_key: str | None
    ) -> tuple[Payment, bool]:
        if idempotency_key is not None:
            existing = await self.repository.get_by_idempotency_key(idempotency_key)
            if existing is not None:
                return existing, False

        tariff = await self.repository.get_tariff(data.tariff_id)
        if tariff is None:
            raise TariffNotFoundError

        discount, amount = calculate_price(tariff.price, data.promo_code)
        schedule = (
            build_schedule(amount, data.installment_months)
            if data.installment_months is not None
            else None
        )
        payment = Payment(
            tariff_id=tariff.id,
            email=str(data.email),
            method=data.method,
            amount=amount,
            discount=discount,
            installment_months=data.installment_months,
            schedule=schedule,
            idempotency_key=idempotency_key,
        )
        return await self.repository.create(payment), True
