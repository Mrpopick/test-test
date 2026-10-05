from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    field_validator,
    model_validator,
)


class TariffResponse(BaseModel):  # get /tariffs
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    price: int


class PaymentCreateRequest(BaseModel):  # post /payments/
    tariff_id: UUID
    email: EmailStr
    method: Literal['card', 'sbp', 'installment']
    installment_months: Literal[3, 6, 12] | None = None
    promo_code: str | None = None

    @field_validator('promo_code')
    @classmethod
    def validate_promo(cls, value: str | None) -> str | None:
        if value is None:
            return None
        norm_value = value.upper()

        if norm_value != 'KVITTO10':
            raise ValueError('Unknown promo!')
        return norm_value

    @model_validator(mode="after")
    def validate_installment(self):
        if self.method == "installment":
            if self.installment_months is None:
                raise ValueError(
                    "installment_months is required for installment"
                )
        elif self.installment_months is not None:
            raise ValueError(
                'installment_months is only for installment'
            )
        return self

class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: Literal[
        'pending',
        'succeeded',
        'failed',
        'refunded',
    ]

    tariff_id: UUID
    amount: int
    discount: int
    method: Literal['card', 'sbp', 'installment']
    installment_months: int | None
    schedule: list[int] | None
    email: EmailStr
    created_at: datetime


class BankWebhookRequest(BaseModel):  # post /webhooks/bank
    payment_id: int
    status: Literal[
        "pending",
        "succeeded",
        "failed",
        "refunded",
    ]


class WebhookSuccessResponse(BaseModel):
    result: Literal['ok']


class InvalidTransitResponse(BaseModel):
    error: Literal['invalid_transition']
