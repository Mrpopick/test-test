def calculate_price(
        price: int,
        promo_code: str | None,
) -> tuple[int, int]:
    if promo_code is None:
        return 0, price

    discount = price * 10 // 100
    amount = price - discount

    return discount, amount


def build_schedule(amount: int, months: int) -> list[int]:
    base_payment, remainder = divmod(amount, months)

    return [
        base_payment + (1 if index < remainder else 0)
        for index in range(months)
    ]
