from __future__ import annotations

import time
from datetime import datetime
from typing import Any

from strategy.ArbitrageStrategy import ArbitrageStrategy
from tools import (
    add_buy_order,
    cache,
    get_info_by_hash_name,
    get_max_buy_order,
    get_my_buy_orders,
    remove_buy_order,
)
from visual import send_webhook_msg


def get_time_str() -> str:
    return datetime.now().strftime("%m/%d %I:%M %p")


def get_buy_order_by_id(buy_order_id: int | str) -> dict[str, Any] | None:
    orders_payload = get_my_buy_orders()
    orders = orders_payload.get("orders", [])

    for order in orders:
        if str(order.get("id")) == str(buy_order_id):
            return order
    return None


def try_update_buy_order(
    buy_order_id: int | str,
    threshold: int,
    delta: int = 1,
    dry_run: bool = False,
    send_updates: bool = True,
) -> None:
    print(f"Attempting to update buy order {buy_order_id}...")
    buy_order = get_buy_order_by_id(buy_order_id)

    if buy_order is None:
        print(f"Buy order {buy_order_id} no longer exists...")
        return

    my_price = int(buy_order["price"])
    item_name = str(buy_order["market_hash_name"])
    _, _, listing_id, _ = get_info_by_hash_name(item_name)
    max_buy_order = get_max_buy_order(listing_id, item_name)

    if my_price > threshold:
        msg = f"Removed order on {item_name} as threshold was exceeded."
        if dry_run:
            print(f"[DRY] would remove order {buy_order_id} on {item_name}")
        else:
            remove_buy_order(buy_order_id, item_name)
            print(msg)
            if send_updates:
                send_webhook_msg(msg)
        return

    print(f"my price: {my_price} | max buy order: {max_buy_order}")

    if max_buy_order <= my_price:
        return

    if max_buy_order + delta <= threshold:
        new_bid = max_buy_order + delta
        msg = f"Updated order on {item_name} from ${round(my_price / 100, 2)} to ${round(new_bid / 100, 2)}."
        if dry_run:
            print(f"[DRY] would replace order {buy_order_id} on {item_name} -> ${round(new_bid / 100, 2)}")
        else:
            remove_buy_order(buy_order_id, item_name)
            add_buy_order(new_bid, 1, item_name=item_name)
            print(msg)
            if send_updates:
                send_webhook_msg(msg)
        return

    msg = f"Removed order on {item_name} as threshold was exceeded."
    if dry_run:
        print(f"[DRY] would remove order {buy_order_id} on {item_name}")
    else:
        remove_buy_order(buy_order_id, item_name)
        print(msg)
        if send_updates:
            send_webhook_msg(msg)


def autobid(threshold: float, delay: int = 20, max_cycles: int | None = None, dry_run: bool = False) -> None:
    cycle = 0
    while True:
        cycle += 1
        buy_orders = get_my_buy_orders().get("orders", [])

        for buy_order in buy_orders:
            try:
                order_id = buy_order["id"]
                item_name = buy_order["market_hash_name"]

                if item_name in cache.data:
                    eq = cache.get(item_name)
                    print("bid data was cached")
                else:
                    result = ArbitrageStrategy([item_name], threshold=threshold, send_alert=False)
                    if result is None:
                        continue
                    _, _, eq, _ = result
                    cache.add(item_name, eq)

                print(eq)
                try_update_buy_order(order_id, int(eq), dry_run=dry_run, send_updates=not dry_run)
                time.sleep(delay)
            except Exception as exc:
                print(exc)
                continue

        if max_cycles is not None and cycle >= max_cycles:
            break
