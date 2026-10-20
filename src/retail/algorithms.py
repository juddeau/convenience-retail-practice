"""Алгоритмы пополнения запасов магазина у дома.

Процедурная реализация: товары, партии и история продаж хранятся
в словарях и списках, каждый алгоритм оформлен отдельной функцией.
"""
import heapq
import math
from datetime import date


def forecast_demand(sales):
    """Алгоритм 1. Средний дневной спрос по истории продаж.

    sales - продажи по дням за расчётное окно. None означает, что
    товара в этот день не было на полке, такой день не учитывается.
    """
    total = 0
    days = 0
    for qty in sales:
        if qty is not None:
            total += qty
            days += 1
    if days == 0:
        return 0.0
    return total / days


def check_batches(batches, demand, today):
    """Алгоритм 2. Контроль сроков годности по правилу FEFO.

    batches - партии одного товара: {"id", "qty", "expires"};
    demand - средний дневной спрос на товар, ед./день;
    today - дата расчёта.
    Возвращает партии к уценке (с количеством, которое не успеет
    продаться до конца срока годности) и партии к списанию.
    """
    heap = []
    for b in batches:
        expires = date.fromisoformat(b["expires"])
        heapq.heappush(heap, (expires, b["id"], b["qty"]))
    markdown = []
    write_off = []
    used = 0.0  # спрос, который заберут партии с более ранним сроком
    while heap:
        expires, batch_id, qty = heapq.heappop(heap)
        days_left = (expires - today).days
        if days_left <= 0:
            write_off.append({"id": batch_id, "qty": qty,
                              "expires": expires})
            continue
        free_demand = max(0.0, demand * days_left - used)
        sold = min(qty, free_demand)
        used += sold
        excess = qty - math.floor(sold)
        if excess > 0:
            markdown.append({"id": batch_id, "qty": excess,
                             "expires": expires, "days_left": days_left})
    return markdown, write_off


def usable_stock(batches, today):
    """Остаток годных к продаже единиц товара на дату расчёта."""
    total = 0
    for b in batches:
        if date.fromisoformat(b["expires"]) > today:
            total += b["qty"]
    return total


def order_quantity(demand, stock, in_transit, lead_time, review,
                   safety_days, pack):
    """Размер заказа по одной позиции с округлением до упаковки."""
    need = demand * (lead_time + review + safety_days) - stock - in_transit
    if need <= 0:
        return 0
    return math.ceil(need / pack) * pack


def build_order(products, forecast, stock, in_transit, categories):
    """Алгоритм 3. Заказ на поставку по всем товарам магазина."""
    order = []
    for p in products:
        code = p["code"]
        safety = categories[p["category"]]["safety_days"]
        qty = order_quantity(forecast[code], stock[code],
                             in_transit.get(code, 0), p["lead_time"],
                             p["review"], safety, p["pack"])
        if qty > 0:
            order.append({"code": code, "name": p["name"], "qty": qty,
                          "supplier": p["supplier"]})
    return order
