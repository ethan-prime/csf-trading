from __future__ import annotations

import time
from typing import Callable

from heuristics.harvey import harvey
from stats import remove_outliers_iqr
from tools import (
    add_buy_order,
    get_info_by_hash_name,
    get_max_buy_order,
    get_sales,
    get_sales_prices,
    price_accurate,
    volume,
)
from visual import send_webhook

FEE = 0.02
HeuristicFn = Callable[[float, int, int], float]


def _write_output_header(path: str) -> None:
    with open(path, "w", encoding="utf-8") as file:
        file.write("Item_Name, Max_Buy_Order, Market_Value, EV, Eq_Value, N_Sales, Volume_7_Days, Heuristic\n")


def _append_output_row(
    path: str,
    item: str,
    max_buy_order: int,
    base_price: int,
    expected_profit: float,
    eq: float,
    n_sales: int,
    vol: int,
    heuristic_value: float,
) -> None:
    with open(path, "a", encoding="utf-8") as file:
        file.write(f"{item}, {max_buy_order}, {base_price}, {expected_profit}, {eq}, {n_sales}, {vol}, {heuristic_value}\n")


def ArbitrageStrategy(
    items: list[str],
    min_price: int = 0,
    max_price: int = 1_000_000,
    threshold: float = 0.03,
    delta: float = 0.01,
    epsilon: int = 10,
    delay: int = 2,
    min_similar_sales: int = 1,
    min_vol: int = 3,
    heuristic: HeuristicFn = harvey,
    require_price_accurate: bool = False,
    write_to_output: str | None = None,
    send_alert: bool = True,
    autobid_ev_threshold: float = 0.07,
    sticker_price_threshold: int = 1000,
) -> tuple[str, int, float, str] | None:
    """Look for buy-order opportunities with positive expected value."""

    if write_to_output:
        _write_output_header(write_to_output)

    single_item_result: tuple[str, int, float, str] | None = None

    for index, item in enumerate(items):
        eta = delay * max(0, len(items) - index - 1)
        print(f"{index + 1}/{len(items)} [~{eta}s remaining...]")
        print(f"Searching {item}")

        try:
            base_price, _, listing_id, icon_path = get_info_by_hash_name(item)
            item_url = f"https://csfloat.com/item/{listing_id}"
            icon_url = f"https://community.cloudflare.steamstatic.com/economy/image/{icon_path}"

            max_buy_order = get_max_buy_order(listing_id, item)
            if max_buy_order <= 0:
                print(f"{item} | skipped: no active buy orders")
                continue

            sales = get_sales(item, sticker_price_threshold=sticker_price_threshold, listing_id=listing_id)
            past_prices = remove_outliers_iqr(get_sales_prices(sales))
            if not past_prices:
                print(f"{item} | skipped: no sale history")
                continue

            expected_profit = base_price * (1 - FEE) - max_buy_order - (delta * 100)
            n_sales = len([price for price in past_prices if price <= max_buy_order + epsilon * 100])
            vol = volume(sales, 7)

            ev_percent = expected_profit / max_buy_order
            heuristic_value = heuristic(ev_percent, n_sales, vol)
            eq = base_price * (1 - FEE) - base_price * threshold

            is_profitable = ev_percent >= threshold
            has_required_sales = n_sales >= min_similar_sales
            is_price_accurate = price_accurate(base_price, past_prices, percent=0.04, verbose=True)
            has_required_volume = vol >= min_vol
            in_price_range = min_price <= max_buy_order + delta <= max_price

            price_gate_ok = is_price_accurate or not require_price_accurate

            if is_profitable and has_required_sales and price_gate_ok and has_required_volume and in_price_range:
                if send_alert:
                    send_webhook(
                        item,
                        round(max_buy_order / 100, 2),
                        round(base_price / 100, 2),
                        round(expected_profit / 100, 2),
                        round(eq / 100, 2),
                        n_sales,
                        vol,
                        heuristic_value,
                        item_url,
                        icon_url,
                    )
                    if ev_percent >= autobid_ev_threshold:
                        add_buy_order(100, 1, item)

                if write_to_output:
                    _append_output_row(
                        write_to_output,
                        item,
                        max_buy_order,
                        base_price,
                        expected_profit,
                        eq,
                        n_sales,
                        vol,
                        heuristic_value,
                    )

            print(
                f"{item} | ev: {round(expected_profit / 100, 2)} | "
                f"similar#: {n_sales} | vol#: {vol} | price acc? {is_price_accurate}"
            )

            if len(items) == 1:
                single_item_result = (item, base_price, eq, icon_url)

        except Exception as exc:
            print(exc)
        finally:
            time.sleep(delay)

    return single_item_result
