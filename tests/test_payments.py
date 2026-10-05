def _payment_data(tariff_id: str, **changes: object) -> dict[str, object]:
    data = {"tariff_id": tariff_id, "email": "user@example.com", "method": "card"}
    data.update(changes)
    return data


def test_amount_with_and_without_lowercase_promo(api_client) -> None:
    client, session = api_client
    data = _payment_data(str(session.tariff.id))

    plain = client.post("/payments", json=data)
    discounted = client.post(
        "/payments", json={**data, "promo_code": "kvitto10"}
    )

    assert plain.status_code == discounted.status_code == 201
    assert (plain.json()["amount"], plain.json()["discount"]) == (1_990_000, 0)
    assert (discounted.json()["amount"], discounted.json()["discount"]) == (
        1_791_000,
        199_000,
    )


def test_installment_schedules_sum_to_amount(api_client) -> None:
    client, session = api_client

    for months in (3, 6, 12):
        response = client.post(
            "/payments",
            json=_payment_data(
                str(session.tariff.id),
                method="installment",
                installment_months=months,
            ),
        )

        assert response.status_code == 201
        payment = response.json()
        assert len(payment["schedule"]) == months
        assert sum(payment["schedule"]) == payment["amount"]


def test_same_idempotency_key_does_not_create_second_payment(api_client) -> None:
    client, session = api_client
    data = _payment_data(str(session.tariff.id))
    headers = {"Idempotency-Key": "same-key"}

    first = client.post("/payments", json=data, headers=headers)
    repeated = client.post("/payments", json=data, headers=headers)

    assert first.status_code == 201
    assert repeated.status_code == 200
    assert repeated.json()["id"] == first.json()["id"]
    assert len(session.payments) == 1


def test_forbidden_transition_returns_409_and_preserves_status(api_client) -> None:
    client, session = api_client
    created = client.post("/payments", json=_payment_data(str(session.tariff.id)))
    assert created.status_code == 201
    payment_id = created.json()["id"]

    response = client.post(
        "/webhooks/bank",
        json={"payment_id": payment_id, "status": "refunded"},
    )
    payment = client.get(f"/payments/{payment_id}")

    assert response.status_code == 409
    assert response.json() == {"error": "invalid_transition"}
    assert payment.status_code == 200
    assert payment.json()["status"] == "pending"


def test_unknown_payment_returns_404(api_client) -> None:
    client, _ = api_client

    response = client.get("/payments/999")

    assert response.status_code == 404