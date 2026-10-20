"""Расчёт пополнения запасов магазина у дома (процедурная версия).

Запуск из корня проекта: python -m src.retail.main
"""
import csv
import json
import os
from datetime import date

from src.retail.algorithms import (build_order, check_batches,
                                   forecast_demand, usable_stock)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
DATA_FILE = os.path.join(BASE_DIR, "data", "store_12.json")


def load_data(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_order(path, order):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Поставщик", "Код товара", "Товар", "Количество"])
        for line in order:
            writer.writerow([line["supplier"], line["code"],
                             line["name"], line["qty"]])


def fmt(d):
    return d.strftime("%d.%m.%Y")


def main():
    data = load_data(DATA_FILE)
    today = date.fromisoformat(data["calc_date"])
    products = data["products"]

    forecast = {}
    for p in products:
        forecast[p["code"]] = forecast_demand(data["sales"][p["code"]])

    stock = {}
    markdown_all = []
    write_off_all = []
    for p in products:
        batches = data["batches"].get(p["code"], [])
        markdown, write_off = check_batches(batches, forecast[p["code"]],
                                            today)
        for b in markdown:
            markdown_all.append((p["name"], b))
        for b in write_off:
            write_off_all.append((p["name"], b))
        stock[p["code"]] = usable_stock(batches, today)

    order = build_order(products, forecast, stock, data["in_transit"],
                        data["categories"])
    ordered = {line["code"]: line["qty"] for line in order}

    print(f"Магазин № {data['store']['id']}, расчёт на {fmt(today)}")
    print("-" * 58)
    print(f"{'Товар':<26}{'Спрос':>8}{'Остаток':>12}{'Заказ':>12}")
    for p in products:
        code = p["code"]
        print(f"{p['name']:<26}{forecast[code]:>8.1f}{stock[code]:>12}"
              f"{ordered.get(code, 0):>12}")
    print("-" * 58)
    print("К уценке:")
    for name, b in markdown_all:
        print(f"  {name}, партия {b['id']}: {b['qty']} ед., годен до "
              f"{fmt(b['expires'])}")
    print("К списанию:")
    for name, b in write_off_all:
        print(f"  {name}, партия {b['id']}: {b['qty']} ед., годен до "
              f"{fmt(b['expires'])}")

    out_file = os.path.join(BASE_DIR, "data",
                            f"order_{today.isoformat()}.csv")
    save_order(out_file, order)
    print(f"Позиций в заказе: {len(order)}, файл: "
          f"{os.path.relpath(out_file, BASE_DIR)}")


if __name__ == "__main__":
    main()
