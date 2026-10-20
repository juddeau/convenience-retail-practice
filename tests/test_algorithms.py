from datetime import date

from src.retail.algorithms import (check_batches, forecast_demand,
                                   order_quantity)


def test_days_without_stock_are_skipped():
    assert forecast_demand([10, None, 14]) == 12


def test_empty_history():
    assert forecast_demand([None, None]) == 0.0


def test_expired_and_excess_batches():
    batches = [{"id": "A", "qty": 5, "expires": "2026-10-27"},
               {"id": "B", "qty": 30, "expires": "2026-10-29"}]
    markdown, write_off = check_batches(batches, 6, date(2026, 10, 27))
    assert [b["id"] for b in write_off] == ["A"]
    assert markdown[0]["qty"] == 18


def test_order_rounded_up_to_pack():
    assert order_quantity(22, 22, 0, 1, 1, 1, 12) == 48


def test_no_order_when_stock_is_enough():
    assert order_quantity(4, 46, 0, 2, 3, 2, 20) == 0
