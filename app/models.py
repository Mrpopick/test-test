from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Integer, String, Uuid, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from app.database import Base


class Tariff(Base):
    __tablename__ = "tariffs"
    __table_args__ = (CheckConstraint("price > 0", name="ck_tariffs_price_positive"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    price: Mapped[int] = mapped_column(BigInteger, nullable=False)

    payments: Mapped[list["Payment"]] = relationship(back_populates="tariff")


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_payments_amount_nonnegative"),
        CheckConstraint("discount >= 0", name="ck_payments_discount_nonnegative"),
        CheckConstraint(
            "status IN ('pending', 'succeeded', 'failed', 'refunded')",
            name="ck_payments_status",
        ),
        CheckConstraint(
            "method IN ('card', 'sbp', 'installment')",
            name="ck_payments_method",
        ),
        CheckConstraint(
            "(method = 'installment' AND installment_months IN (3, 6, 12) AND schedule IS NOT NULL) "
            "OR (method <> 'installment' AND installment_months IS NULL AND schedule IS NULL)",
            name="ck_payments_installment_fields",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", server_default="pending")
    tariff_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("tariffs.id"), nullable=False
    )
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    discount: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, server_default="0")
    method: Mapped[str] = mapped_column(String(20), nullable=False)
    installment_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    schedule: Mapped[list[int] | None] = mapped_column(ARRAY(BigInteger), nullable=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    tariff: Mapped[Tariff] = relationship(back_populates="payments")
