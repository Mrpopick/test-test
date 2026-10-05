from collections.abc import Iterator
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

import main
from app.dependencies import get_session
from app.models import Payment, Tariff


class MemorySession:
    def __init__(self) -> None:
        self.tariff = Tariff(id=uuid4(), title="standard", price=1_990_000)
        self.payments: dict[int, Payment] = {}
        self.pending: Payment | None = None

    async def get(self, model: type, key: object) -> Tariff | Payment | None:
        if model is Tariff:
            return self.tariff if key == self.tariff.id else None
        if model is Payment:
            return self.payments.get(key)
        return None

    async def scalar(self, statement: object) -> Payment | None:
        key = next(iter(statement.compile().params.values()))
        return next(
            (payment for payment in self.payments.values() if payment.idempotency_key == key),
            None,
        )

    def add(self, payment: Payment) -> None:
        self.pending = payment

    async def flush(self) -> None:
        payment = self.pending
        payment.id = len(self.payments) + 1
        payment.status = "pending"
        payment.created_at = datetime.now(timezone.utc)
        self.payments[payment.id] = payment
        self.pending = None

    async def refresh(self, payment: Payment) -> None:
        pass


@pytest.fixture
def api_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[tuple[TestClient, MemorySession]]:
    async def skip_database_startup() -> None:
        pass

    monkeypatch.setattr(main, "initialize_database", skip_database_startup)
    session = MemorySession()
    main.app.dependency_overrides[get_session] = lambda: session
    try:
        with TestClient(main.app) as client:
            yield client, session
    finally:
        main.app.dependency_overrides.pop(get_session, None)